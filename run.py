"""
Convenience startup script.

Usage:
    python run.py              # development (auto-reload)
    python run.py --prod       # production (no reload, multiple workers)
"""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Start the Finance Tracker API server")
    parser.add_argument("--prod",   action="store_true", help="Run in production mode")
    parser.add_argument("--host",   default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port",   default="8000",       help="Bind port (default: 8000)")
    parser.add_argument("--workers",default="4",          help="Worker count for --prod (default: 4)")
    args = parser.parse_args()

    base_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", args.host,
        "--port", args.port,
    ]

    if args.prod:
        cmd = base_cmd + ["--workers", args.workers]
        print(f"Starting in PRODUCTION mode on http://{args.host}:{args.port} ({args.workers} workers)")
    else:
        cmd = base_cmd + ["--reload"]
        print(f"Starting in DEVELOPMENT mode on http://{args.host}:{args.port} (auto-reload enabled)")

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
