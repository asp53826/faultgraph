"""Research and local-service command line."""

from __future__ import annotations

import argparse
import json

import uvicorn

from faultgraph.engine import analyze, benchmark
from faultgraph.scenarios import bundled_incidents


def main() -> None:
    parser = argparse.ArgumentParser(prog="faultgraph")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("benchmark")
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("incident_id")
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    incidents = bundled_incidents()
    if args.command == "benchmark":
        print(benchmark(incidents).model_dump_json(indent=2))
    elif args.command == "analyze":
        incident = next((item for item in incidents if item.id == args.incident_id), None)
        if incident is None:
            raise SystemExit(f"unknown incident {args.incident_id}")
        print(analyze(incident).model_dump_json(indent=2))
    elif args.command == "serve":
        print(json.dumps({"service": "faultgraph", "url": f"http://{args.host}:{args.port}"}))
        uvicorn.run("faultgraph.api:app", host=args.host, port=args.port, reload=args.reload)
