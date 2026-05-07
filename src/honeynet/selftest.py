from __future__ import annotations

from pathlib import Path
from time import time_ns

from .analytics import summarize
from .storage import EventStore


def main() -> int:
    test_dir = Path.cwd() / "data" / f"selftest-{time_ns()}"
    store = EventStore(test_dir)
    try:
        first = store.add_event(event_type="connection", service="telnet", src_ip="127.0.0.1", src_port=50100)
        second = store.add_event(
            event_type="command",
            service="telnet",
            src_ip="127.0.0.1",
            src_port=50100,
            command="cat /etc/passwd",
        )
        events = store.list_events(limit=10)
        assert len(events) == 2, events
        assert first["id"] < second["id"]
        summary = summarize(events)
        assert summary["total_events"] == 2
        assert any(name == "Account Discovery" for name, _count in summary["techniques"])
    finally:
        store.close()
    print("selftest passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
