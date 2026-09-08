#!/usr/bin/env python3
"""Build and execute UserAlarm host tests without changing DUT sources."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DUT = ROOT / "DUT" / "L04_FB" / "UserAlarm"
BUILD = ROOT / "build" / "UserAlarm"
MIRROR_DUT = BUILD / "DUT"
MIRROR_FB = MIRROR_DUT / "L04_FB" / "UserAlarm"

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
        str(ROOT / "Test" / "UserAlarm" / "test_user_alarm.c"),
        "-o", str(executable),
    ]
    print(" ".join(command))
    build = subprocess.run(command, cwd=ROOT, check=False)
    if build.returncode != 0:
        return build.returncode
    return subprocess.run([str(executable)], cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
