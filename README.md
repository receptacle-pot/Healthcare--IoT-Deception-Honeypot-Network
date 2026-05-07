# Healthcare IoT Deception Honeypot Network

A real-time, low-interaction deception lab for healthcare IoT security research. It simulates vulnerable medical and facility IoT devices, captures attacker behavior, extracts indicators of compromise, and streams live intelligence to a browser dashboard.

This project is intentionally safe by default:

- No real shell is exposed.
- All services are fake low-interaction traps.
- All payloads are logged as metadata and bytes, not executed.
- The default ports are unprivileged local lab ports.

## Features

- Simulated medical IoT services:
  - `2222` SSH banner trap
  - `2223` Telnet-style vitals monitor shell
  - `8081` unauthenticated biomedical web panel
  - `1883` MQTT telemetry broker trap
  - `2104` DICOM association trap
- Real-time logging to SQLite and JSONL.
- Live dashboard with:
  - Attack timeline
  - Source IP and service breakdowns
  - Command and credential intelligence
  - Lightweight geolocation enrichment
  - MITRE-style technique hints
- Demo traffic generator for local testing.
- Docker and Docker Compose deployment.
- Mermaid architecture diagram and four-week roadmap artifacts.

## Quick Start

Create a virtual environment and install Flask:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If your machine uses `python` instead of `py`, replace `py` with `python`.

From this folder:

```powershell
python -m src.honeynet
```

Then open:

- Dashboard: http://127.0.0.1:8000
- Fake device web panel: http://127.0.0.1:8081

Generate safe demo attacker traffic in another terminal:

```powershell
python -m src.honeynet.demo_attack
```

Run the smoke test:

```powershell
python -m src.honeynet.selftest
```

## Docker

```powershell
docker compose up --build
```

Dashboard:

```text
http://127.0.0.1:8000
```

## Project Layout

```text
src/honeynet/
  __main__.py          Entry point
  honeypot.py          Fake IoT services
  dashboard.py         Realtime dashboard HTTP/SSE server
  storage.py           SQLite and JSONL event store
  analytics.py         Summary and technique extraction
  geo.py               Offline IP enrichment
  demo_attack.py       Safe local traffic generator
  selftest.py          Dependency-free smoke tests
  static/              Dashboard frontend
docs/
  architecture.md
  analytical-report.md
```

## Safety Notes

Only expose this outside a controlled lab after explicit approval and network isolation review. Use a VM, cloud sandbox, or Docker network with strict firewall rules. Do not run this on a production hospital network without segmentation and change approval.
