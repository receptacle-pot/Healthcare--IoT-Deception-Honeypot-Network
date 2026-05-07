# Architecture

## Runtime View

```mermaid
flowchart LR
  Attacker["Scanner / Attacker VM"] --> SSH["SSH banner trap :2222"]
  Attacker --> Telnet["Telnet medical shell :2223"]
  Attacker --> Web["Fake device web panel :8081"]
  Attacker --> MQTT["MQTT telemetry trap :1883"]
  Attacker --> DICOM["DICOM association trap :2104"]

  SSH --> Store["SQLite + JSONL event store"]
  Telnet --> Store
  Web --> Store
  MQTT --> Store
  DICOM --> Store

  Store --> Analytics["Python analytics and IoC extraction"]
  Analytics --> Flask["Flask API + SSE :8000"]
  Flask --> Dashboard["Realtime dashboard"]
```

## Components

| Component | Technology | Purpose |
| --- | --- | --- |
| Honeypot listeners | Python sockets and HTTP server | Simulate vulnerable healthcare IoT services without exposing a real shell |
| Dashboard API | Flask | Serve JSON endpoints, export data, and stream events with Server-Sent Events |
| Data store | SQLite and JSONL | Durable event storage for analysis and audit evidence |
| Frontend | HTML, CSS, JavaScript | Live threat dashboard for researchers and administrators |
| Containerization | Docker Compose | Isolated, repeatable lab deployment |

## Deception Profile

The default simulated asset is `MediVitals VX-1200`, a fictional patient vitals monitor located in `ICU-West-3`. It exposes common attacker magnets: old SSH banners, Telnet maintenance access, a weak web login panel, MQTT telemetry, and DICOM-like imaging traffic.

## Safety Boundary

The shell is fake. Commands are parsed, logged, and answered with static responses. URLs and upload attempts are saved as indicators, but no downloaded content is executed. The deployment should still be treated as hostile-facing infrastructure and placed in a segmented lab network.

