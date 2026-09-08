#!/usr/bin/env python3
"""Build UserAlarm host tests, write TestResult, and copy latest report to DUT."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RELATIVE_FB = Path("L04_FB") / "UserAlarm"
DUT = ROOT / "DUT" / RELATIVE_FB
TEST = ROOT / "Test" / RELATIVE_FB
RESULT = ROOT / "TestResult" / RELATIVE_FB
DUT_REPORT = DUT / "TestReport"
BUILD = ROOT / "build" / RELATIVE_FB
MIRROR_DUT = BUILD / "DUT"
MIRROR_FB = MIRROR_DUT / RELATIVE_FB

DEFINE_H = """#ifndef SSM_STD_DEFINE_H
#define SSM_STD_DEFINE_H
#include <stdbool.h>
#include <stdint.h>
#define MY_API
#endif
"""

LIB_H = """#ifndef SSM_STD_FB_LIB_H
#define SSM_STD_FB_LIB_H
#include "ssm_std_define.h"
#include "L04_FB/UserAlarm/userAlarm.h"
#endif
"""


def git_commit() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False
    )
    return proc.stdout.strip() if proc.returncode == 0 else "LOCAL"


def write_reports(status: str, exit_code: int, compiler: str,
                  build_output: str, test_output: str) -> Path:
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    tested_at = now.isoformat(timespec="seconds")
    RESULT.mkdir(parents=True, exist_ok=True)
    DUT_REPORT.mkdir(parents=True, exist_ok=True)

    report_path = RESULT / f"UserAlarm_TestReport_{timestamp}.md"
    report = f"""# UserAlarm Unit Test Report

- Result: **{status}**
- Test author: OpenAI Codex
- DUT author: CH
- Tested at UTC: {tested_at}
- Source commit: `{git_commit()}`
- Compiler: `{compiler}`
- Random seed: `20260903`
- Expected checks: 10,027

## Test output

```text
{test_output.strip() or "(no test output)"}
```

## Compiler output

```text
{build_output.strip() or "(no compiler warnings)"}
```

## Known interface findings

1. No public Init API.
2. No NULL pointer validation.
3. AlarmH and AlarmL legal ranges are not defined.
4. Invalid Mode silently behaves as Disable.
5. The return value is always 1.
6. Clear-mask operations produce strict sign-conversion warnings.
7. alarmLatch is shared by hysteresis and HOLD.
"""
    report_path.write_text(report, encoding="utf-8")
    shutil.copy2(report_path, DUT_REPORT / "latest.md")

    summary = {
        "schema_version": 1,
        "function_block": "UserAlarm",
        "status": status,
        "exit_code": exit_code,
        "tested_at_utc": tested_at,
        "source_commit": git_commit(),
        "checks": 10027,
        "random_vectors": 5000,
        "random_seed": 20260903,
        "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
        "dut_report_copy": str((DUT_REPORT / "latest.md").relative_to(ROOT)).replace("\\", "/"),
    }
    (RESULT / "latest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return report_path


def main() -> int:
    compiler = os.environ.get("CC", "gcc")
    if shutil.which(compiler) is None:
        print(f"Compiler not found: {compiler}", file=sys.stderr)
        return 2

    MIRROR_FB.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DUT / "userAlarm.c", MIRROR_FB / "userAlarm.c")
    shutil.copy2(DUT / "userAlarm.h", MIRROR_FB / "userAlarm.h")
    (MIRROR_DUT / "ssm_std_define.h").write_text(DEFINE_H, encoding="utf-8")
    (MIRROR_DUT / "ssm_std_FB_lib.h").write_text(LIB_H, encoding="utf-8")

    executable = BUILD / ("test_user_alarm.exe" if os.name == "nt" else "test_user_alarm")
    command = [
        compiler, "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
        "-I", str(MIRROR_FB),
        str(MIRROR_FB / "userAlarm.c"),
        str(TEST / "test_user_alarm.c"),
        "-o", str(executable),
    ]
    print(" ".join(command))
    build = subprocess.run(
        command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )
    print(build.stdout, end="")
    if build.returncode != 0:
        report = write_reports("BUILD_FAIL", build.returncode, compiler, build.stdout, "")
        print(f"Report: {report}")
        return build.returncode

    test = subprocess.run(
        [str(executable)], cwd=ROOT, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=False
    )
    print(test.stdout, end="")
    status = "FUNCTIONAL_PASS_WITH_FINDINGS" if test.returncode == 0 else "FAIL"
    report = write_reports(status, test.returncode, compiler, build.stdout, test.stdout)
    print(f"Report: {report}")
    print(f"DUT copy: {DUT_REPORT / 'latest.md'}")
    return test.returncode


if __name__ == "__main__":
    raise SystemExit(main())
