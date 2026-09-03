from __future__ import annotations
import csv
import json
from pathlib import Path
import pytest
from test_adapter import DutAdapter

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "Specification" / "test_vectors.csv"


def _cases() -> list[dict[str, str]]:
    with VECTORS.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


CASES = _cases()


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["test_id"])
def test_vector(case: dict[str, str]) -> None:
    dut = DutAdapter()
    dut.init()

    if case["category"] == "initialization":
        actual_output = dut.snapshot()
        actual_error = actual_output.pop("error", "FB_ERROR_NONE")
    else:
        actual_output, actual_error = dut.execute(
            json.loads(case["input_json"]),
            json.loads(case["parameter_json"]),
        )

    expected = json.loads(case["expected_output_json"])
    tolerance = float(case["tolerance"])

    assert actual_error == case["expected_error"]
    assert actual_output.keys() >= expected.keys()
    for name, expected_value in expected.items():
        actual_value = actual_output[name]
        if isinstance(expected_value, (int, float)):
            assert actual_value == pytest.approx(expected_value, abs=tolerance)
        else:
            assert actual_value == expected_value
