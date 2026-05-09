from __future__ import annotations
from collections import Counter
from typing import Any

TECHNIQUE_HINTS = {
    "wget": "Ingress Tool Transfer",
    "curl": "Ingress Tool Transfer",
    "busybox": "Unix Shell Discovery",
    "uname": "System Information Discovery",
    "cat /etc/passwd": "Account Discovery",
    "ifconfig": "System Network Configuration Discovery",
    "ip addr": "System Network Configuration Discovery",
    "chmod": "Permission Modification",
    "sh ": "Command and Scripting Interpreter",
    "python": "Command and Scripting Interpreter",
}


def classify_command(command: str) -> str:
    lowered = command.lower()
    for marker, technique in TECHNIQUE_HINTS.items():
        if marker in lowered:
            return technique
    if command:
        return "Interactive Command"
    return "Reconnaissance"


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    services = Counter(event.get("service") or "unknown" for event in events)
    event_types = Counter(event.get("event_type") or "unknown" for event in events)
    src_ips = Counter(event.get("src_ip") or "unknown" for event in events)
    usernames = Counter(event.get("username") for event in events if event.get("username"))
    commands = Counter(event.get("command") for event in events if event.get("command"))
    techniques = Counter()

    for event in events:
        if event.get("command"):
            techniques[classify_command(event["command"])] += 1
        elif event.get("event_type") in {"http_request", "connection", "mqtt_probe", "dicom_probe"}:
            techniques["Reconnaissance"] += 1

    return {
        "total_events": len(events),
        "services": services.most_common(),
        "event_types": event_types.most_common(),
        "src_ips": src_ips.most_common(10),
        "usernames": usernames.most_common(10),
        "commands": commands.most_common(10),
        "techniques": techniques.most_common(10),
    }


def risk_score(event_type: str, command: str | None = None, payload: str | None = None) -> int:
    score = 10
    if event_type in {"auth_attempt", "http_login"}:
        score += 20
    if event_type in {"command", "payload_url", "upload"}:
        score += 40
    sample = " ".join(part for part in [command or "", payload or ""] if part).lower()
    if any(marker in sample for marker in ["wget", "curl", "chmod", "busybox", "/etc/passwd"]):
        score += 25
    return min(score, 100)

