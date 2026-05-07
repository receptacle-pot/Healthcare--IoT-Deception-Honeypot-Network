from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    bind_host: str
    dashboard_port: int
    web_panel_port: int
    ssh_banner_port: int
    telnet_port: int
    mqtt_port: int
    dicom_port: int
    data_dir: Path


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def load_settings() -> Settings:
    data_dir = Path(os.getenv("HONEYPOT_DATA_DIR", "data")).resolve()
    return Settings(
        bind_host=os.getenv("HONEYPOT_BIND", "0.0.0.0"),
        dashboard_port=env_int("HONEYPOT_DASHBOARD_PORT", 8000),
        web_panel_port=env_int("HONEYPOT_WEB_PORT", 8081),
        ssh_banner_port=env_int("HONEYPOT_SSH_PORT", 2222),
        telnet_port=env_int("HONEYPOT_TELNET_PORT", 2223),
        mqtt_port=env_int("HONEYPOT_MQTT_PORT", 1883),
        dicom_port=env_int("HONEYPOT_DICOM_PORT", 2104),
        data_dir=data_dir,
    )

