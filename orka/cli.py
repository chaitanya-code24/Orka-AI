import argparse
import json
from pathlib import Path

import uvicorn

from orka import OrkaAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orka", description="Orka AI command line interface.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a query through the Orka framework.")
    run_parser.add_argument("query", help="Natural language task to execute.")
    run_parser.add_argument("--config", default="config.json", help="Path to the Orka config file.")

    serve_parser = subparsers.add_parser("serve", help="Start the Orka FastAPI server.")
    serve_parser.add_argument("--config", default="config.json", help="Path to the Orka config file.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to listen on.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        agent = OrkaAgent(args.config)
        result = agent.run(args.query)
        print(json.dumps(result, indent=2))
        return

    if args.command == "serve":
        import os

        os.environ["ORKA_CONFIG_PATH"] = str(Path(args.config))
        uvicorn.run("orka.main:app", host=args.host, port=args.port, reload=False)
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
