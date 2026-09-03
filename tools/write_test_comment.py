#!/usr/bin/env python3
"""Insert or replace a generated test-result comment in a C source/header."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

BEGIN = "/* UNIT_TEST_RESULT_BEGIN"
END = "UNIT_TEST_RESULT_END */"


def render(result: dict) -> str:
    lines = [
        BEGIN,
        " * Generated record — do not edit inside this block.",
        f" * Test item    : {result.get('test_item', 'Function Block unit test')}",
        f" * Result       : {result['status']}",
        f" * Test author  : {result['author']}",
        f" * Tested at UTC: {result['tested_at_utc']}",
        f" * Source commit: {result.get('source_commit', 'UNKNOWN')}",
        f" * Report       : {result.get('report', 'TestResult/latest.json')}",
        f" * Exit code    : {result.get('exit_code', 'UNKNOWN')}",
        f" * {END}",
        "",
    ]
    return "\n".join(lines)


def update(source: Path, block: str) -> None:
    text = source.read_text(encoding="utf-8")
    begin = text.find(BEGIN)
    if begin >= 0:
        end = text.find(END, begin)
        if end < 0:
            raise ValueError(f"Unclosed unit-test marker in {source}")
        end += len(END)
        while end < len(text) and text[end] in "\r\n":
            end += 1
        text = text[:begin] + block + text[end:]
    else:
        text = block + text
    source.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help=".c or .h file to annotate")
    parser.add_argument("--result", type=Path, default=Path("TestResult/latest.json"))
    args = parser.parse_args()

    if args.source.suffix.lower() not in {".c", ".h"}:
        parser.error("source must be a .c or .h file")
    result = json.loads(args.result.read_text(encoding="utf-8"))
    update(args.source, render(result))
    print(f"Updated test-result comment: {args.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
