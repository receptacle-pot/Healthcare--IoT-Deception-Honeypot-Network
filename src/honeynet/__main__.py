from __future__ import annotations

import signal
import sys
from threading import Event

from .config import load_settings
from .dashboard import create_app
from .honeypot import build_honeypot_network
from .storage import EventStore


def main() -> int:
    settings = load_settings()
    store = EventStore(settings.data_dir)
    ports = {
        "ssh": settings.ssh_banner_port,
        "telnet": settings.telnet_port,
        "mqtt": settings.mqtt_port,
        "dicom": settings.dicom_port,
        "http": settings.web_panel_port,
    }
    network = build_honeypot_network(settings.bind_host, store, ports)
    stop_event = Event()

    def stop(_signum=None, _frame=None) -> None:
        stop_event.set()
        network.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    network.start()
    store.add_event(
        event_type="system",
        service="controller",
        src_ip="127.0.0.1",
        payload="Healthcare IoT honeypot network started",
        raw={"ports": ports, "dashboard": settings.dashboard_port},
    )

    print("Healthcare IoT Deception Honeypot Network")
    print(f"Dashboard: http://127.0.0.1:{settings.dashboard_port}")
    print(f"Fake web panel: http://127.0.0.1:{settings.web_panel_port}")
    print(f"SSH banner trap: {settings.ssh_banner_port}")
    print(f"Telnet shell trap: {settings.telnet_port}")
    print(f"MQTT trap: {settings.mqtt_port}")
    print(f"DICOM trap: {settings.dicom_port}")

    app = create_app(store)
    try:
        app.run(host=settings.bind_host, port=settings.dashboard_port, threaded=True, use_reloader=False)
    finally:
        stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())

