#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author", required=True)
    parser.add_argument("--source-commit", default=os.getenv("GITHUB_SHA", "LOCAL"))
    parser.add_argument("--result", default="TestResult/latest.json")
    args, pytest_args = parser.parse_known_args()

    command = [sys.executable, "-m", "pytest", "Test", "-q", *pytest_args]
    completed = subprocess.run(command, check=False)

    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema_version": 1,
        "test_item": "Function Block unit test",
        "author": args.author,
        "tested_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": args.source_commit,
        "command": command,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "exit_code": completed.returncode,
    }
    result_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Result: {result_path} ({summary['status']})")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
