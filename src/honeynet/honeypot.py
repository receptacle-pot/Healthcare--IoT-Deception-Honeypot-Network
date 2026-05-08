from __future__ import annotations

import html
import re
import socketserver
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import parse_qs

from .sensor_profiles import DEVICE_PROFILE, FAKE_FILES, SHELL_RESPONSES
from .storage import EventStore


def peer(handler: socketserver.BaseRequestHandler) -> tuple[str, int]:
    host, port = handler.client_address[:2]
    return str(host), int(port)


def clean_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").replace("\x00", "").strip()


class ManagedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, handler_cls, store: EventStore):
        self.store = store
        super().__init__(server_address, handler_cls)


class SSHBannerTrap(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        src_ip, src_port = peer(self)
        store: EventStore = self.server.store
        store.add_event(event_type="connection", service="ssh", src_ip=src_ip, src_port=src_port)
        self.request.sendall(b"SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.8\r\n")
        
        try:
            data = self.request.recv(512)
        except OSError:
            data = b""
        
        if data:
            store.add_event(
                event_type="ssh_probe",
                service="ssh",
                src_ip=src_ip,
                src_port=src_port,
                payload=clean_text(data),
                raw={"bytes": list(data[:64])},
            )


class TelnetMedicalShell(socketserver.BaseRequestHandler):
    prompt = b"root@medivitals-vx1200:/# "

    def write(self, value: str | bytes) -> None:
        self.request.sendall(value if isinstance(value, bytes) else value.encode("utf-8"))

    def read_line(self, limit: int = 2048) -> str:
        data = bytearray()
        
        while len(data) < limit:
            chunk = self.request.recv(1)
            if not chunk:
                break
            if chunk in {b"\n", b"\r"}:
                if data:
                    break
                continue
            data.extend(chunk)
        return clean_text(bytes(data))

    def handle(self) -> None:
        src_ip, src_port = peer(self)
        store: EventStore = self.server.store
        store.add_event(event_type="connection", service="telnet", src_ip=src_ip, src_port=src_port)

        self.write(f"{DEVICE_PROFILE['name']} telemetry console\r\nlogin: ")
        username = self.read_line()
        self.write("Password: ")
        password = self.read_line()
        store.add_event(
            event_type="auth_attempt",
            service="telnet",
            src_ip=src_ip,
            src_port=src_port,
            username=username,
            password=password,
        )
        self.write("\r\nVXOS maintenance shell ready\r\n")

        for _ in range(24):
            self.write(self.prompt)
            command = self.read_line()
            if not command:
                break
            store.add_event(event_type="command", service="telnet", src_ip=src_ip, src_port=src_port, command=command)
            lowered = command.lower()
            if lowered in {"exit", "quit", "logout"}:
                self.write("logout\r\n")
                break
            self.write(self.respond(command))

    def respond(self, command: str) -> str:
        stripped = command.strip()
        lowered = stripped.lower()
        if lowered.startswith("cat "):
            path = stripped.split(maxsplit=1)[1]
            return FAKE_FILES.get(path, f"cat: {path}: No such file or directory\n").replace("\n", "\r\n")
        if "wget" in lowered or "curl" in lowered:
            urls = re.findall(r"https?://[^\s;]+", stripped)
            for url in urls:
                src_ip, src_port = peer(self)
                self.server.store.add_event(
                    event_type="payload_url",
                    service="telnet",
                    src_ip=src_ip,
                    src_port=src_port,
                    command=stripped,
                    payload=url,
                )
            return "Connecting... saved to /tmp/update.bin\r\n"
        return SHELL_RESPONSES.get(lowered, f"sh: {html.escape(stripped)}: command not found\n").replace("\n", "\r\n")


class MQTTTrap(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        src_ip, src_port = peer(self)
        try:
            data = self.request.recv(1024)
        except OSError:
            data = b""
        event_type = "mqtt_probe"
        if data and data[0] >> 4 == 1:
            event_type = "mqtt_connect"
        self.server.store.add_event(
            event_type=event_type,
            service="mqtt",
            src_ip=src_ip,
            src_port=src_port,
            payload=clean_text(data),
            raw={"hex": data[:80].hex()},
        )
        if data:
            self.request.sendall(b"\x20\x02\x00\x00")


class DICOMTrap(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        src_ip, src_port = peer(self)
        try:
            data = self.request.recv(2048)
        except OSError:
            data = b""
        self.server.store.add_event(
            event_type="dicom_probe",
            service="dicom",
            src_ip=src_ip,
            src_port=src_port,
            payload=clean_text(data[:160]),
            raw={"hex": data[:120].hex()},
        )
        if data:
            self.request.sendall(b"\x03\x00\x00\x00")


class WebPanelServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, handler_cls, store: EventStore):
        self.store = store
        super().__init__(server_address, handler_cls)


class MedicalWebPanel(BaseHTTPRequestHandler):
    server_version = "Boa/0.94.14rc21"

    def log_message(self, format: str, *args) -> None:
        return

    def _record(self, event_type: str, body: str | None = None, username: str | None = None, password: str | None = None) -> None:
        src_ip, src_port = self.client_address[:2]
        self.server.store.add_event(
            event_type=event_type,
            service="http",
            src_ip=str(src_ip),
            src_port=int(src_port),
            username=username,
            password=password,
            method=self.command,
            path=self.path,
            user_agent=self.headers.get("User-Agent"),
            payload=body,
            raw={"headers": dict(self.headers)},
        )

    def do_GET(self) -> None:
        self._record("http_request")
        if self.path.startswith("/api/vitals"):
            self._json({"heart_rate": 78, "spo2": 98, "temperature_c": 36.8, "bed": "ICU-W-03"})
            return
        self._html(self.panel())

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(min(length, 100_000)).decode("utf-8", errors="replace")
        fields = parse_qs(body)
        username = fields.get("username", fields.get("user", [""]))[0]
        password = fields.get("password", fields.get("pass", [""]))[0]
        event_type = "http_login" if "login" in self.path else "upload"
        self._record(event_type, body=body[:5000], username=username or None, password=password or None)
        if event_type == "http_login":
            self._html(self.panel("Authentication failed; maintenance lockout active."), status=HTTPStatus.UNAUTHORIZED)
        else:
            self._html(self.panel("Firmware package queued for validation."))

    def _json(self, data: dict) -> None:
        import json

        encoded = json.dumps(data).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def panel(self, message: str = "") -> str:
        notice = f"<p class='notice'>{html.escape(message)}</p>" if message else ""
        return f"""<!doctype html>
<html><head><title>{DEVICE_PROFILE['name']}</title>
<style>body{{font-family:Arial,sans-serif;background:#eef3f6;margin:0;color:#14212b}}main{{max-width:720px;margin:48px auto;background:white;border:1px solid #cfd8df;padding:24px}}label{{display:block;margin-top:12px}}input{{padding:8px;width:260px}}button{{margin-top:16px;padding:8px 14px}}.notice{{color:#9b1c1c}}code{{background:#edf2f7;padding:2px 6px}}</style>
</head><body><main>
<h1>{DEVICE_PROFILE['name']}</h1>
<p>Vendor: {DEVICE_PROFILE['vendor']} | Firmware: <code>{DEVICE_PROFILE['firmware']}</code> | Location: {DEVICE_PROFILE['location']}</p>
{notice}
<form method="post" action="/login.cgi">
<label>Username <input name="username" value="admin"></label>
<label>Password <input name="password" type="password" value="admin"></label>
<button>Login</button>
</form>
<form method="post" action="/firmware/upload" enctype="application/octet-stream">
<label>Firmware URL <input name="url" value="http://updates.example/vx.bin"></label>
<button>Upload</button>
</form>
<p>Telemetry endpoint: <code>/api/vitals</code></p>
</main></body></html>"""


class HoneypotNetwork:
    def __init__(self, bind_host: str, store: EventStore):
        self.bind_host = bind_host
        self.store = store
        self.servers: list[tuple[str, int, object]] = []
        self.threads: list[threading.Thread] = []

    def add_tcp(self, name: str, port: int, handler_cls: type[socketserver.BaseRequestHandler]) -> None:
        server = ManagedTCPServer((self.bind_host, port), handler_cls, self.store)
        self.servers.append((name, port, server))

    def add_http_panel(self, port: int) -> None:
        server = WebPanelServer((self.bind_host, port), MedicalWebPanel, self.store)
        self.servers.append(("http", port, server))

    def start(self) -> None:
        for name, port, server in self.servers:
            thread = threading.Thread(target=server.serve_forever, name=f"{name}:{port}", daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self) -> None:
        for _, _, server in self.servers:
            server.shutdown()
            server.server_close()


def build_honeypot_network(bind_host: str, store: EventStore, ports: dict[str, int]) -> HoneypotNetwork:
    network = HoneypotNetwork(bind_host, store)
    network.add_tcp("ssh", ports["ssh"], SSHBannerTrap)
    network.add_tcp("telnet", ports["telnet"], TelnetMedicalShell)
    network.add_tcp("mqtt", ports["mqtt"], MQTTTrap)
    network.add_tcp("dicom", ports["dicom"], DICOMTrap)
    network.add_http_panel(ports["http"])
    return network

