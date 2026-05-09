from __future__ import annotations
import json
import time
from typing import Any
from flask import Flask, Response, jsonify, render_template, request, stream_with_context
from .analytics import summarize
from .storage import EventStore


def create_app(store: EventStore) -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/api/events")
    def events():
        limit = request.args.get("limit", default=200, type=int)
        after_id = request.args.get("after_id", default=None, type=int)
        return jsonify(store.list_events(limit=limit, after_id=after_id))

    @app.get("/api/summary")
    def summary():
        events = store.list_events(limit=1000)
        return jsonify(summarize(events))

    @app.get("/api/stream")
    def stream():
        initial_last_id = request.args.get("after_id", default=0, type=int) or 0

        @stream_with_context
        def generate():
            last_id = initial_last_id
            while True:
                new_events = store.list_events(limit=100, after_id=last_id)
                for event in new_events:
                    last_id = max(last_id, int(event["id"]))
                    yield f"id: {event['id']}\n"
                    yield "event: honeypot-event\n"
                    yield f"data: {json.dumps(event)}\n\n"
                yield ": heartbeat\n\n"
                time.sleep(1)

        return Response(generate(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/api/export.json")
    def export_json():
        return jsonify(store.list_events(limit=1000))

    @app.get("/healthz")
    def healthz() -> dict[str, Any]:
        return {"status": "ok"}

    return app
