"""DUT adapter.

Customize only this file for each Function Block.  It isolates pytest from the
actual C ABI. Use ctypes to load build/libfb_under_test.so (or .dll on Windows).
"""
from __future__ import annotations
from typing import Any


class DutAdapter:
    def __init__(self) -> None:
        self._state: dict[str, Any] = {"output": 0, "error": "FB_ERROR_NONE"}

    def init(self) -> None:
        """Call FB_xxx_Init through ctypes here."""
        self._state = {"output": 0, "error": "FB_ERROR_NONE"}

    def execute(
        self, inputs: dict[str, Any], parameters: dict[str, Any]
    ) -> tuple[dict[str, Any], str]:
        """Call FB_xxx_Execute and return (outputs, error-name).

        The placeholder deliberately raises so an unconnected DUT cannot
        accidentally be reported as passing.
        """
        raise NotImplementedError("Connect DutAdapter.execute() to the C Function Block")

    def snapshot(self) -> dict[str, Any]:
        """Optionally expose observable state for state-transition tests."""
        return dict(self._state)
