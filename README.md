# myUnit_TestTool — branch_1

Python-based unit-test scaffold for portable embedded C Function Blocks.

## Directory layout

```text
DUT/                         # Put the tested .c/.h and dependencies here
Specification/
  interface_spec.yaml        # Machine-readable interface and contract
  test_vectors.csv           # Formal input/output vectors
Test/
  test_adapter.py            # ctypes/C ABI adapter customized per FB
  test_function_block.py     # pytest vector runner
  mocks/                     # Hardware and external dependency mocks
tools/
  run_tests.py               # Executes tests and writes JSON summary
  write_test_comment.py      # Inserts/replaces bounded comment in .c/.h
TestResult/                  # Test evidence
```

## Recommended specification format

Use YAML for input/output/parameter types, valid ranges, error codes, Init,
cycle time and contracts. Use CSV for formal test vectors and traceability.
Use Markdown only for explanations, equations, timing/state diagrams and review
notes. This keeps the specification readable and executable.

## Quick start

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python tools/run_tests.py --author "Your Name"
python tools/write_test_comment.py DUT/FB_xxx/FB_xxx.c
```

Before running functional cases, replace the placeholder implementation in
`Test/test_adapter.py` with ctypes calls to the compiled DUT. The adapter
raises `NotImplementedError` by design, so an unconnected FB cannot be falsely
reported as PASS.

## Source annotation policy

The generated source comment records test item, PASS/FAIL, author, UTC time,
source commit, report path and exit code. Only the text between
`UNIT_TEST_RESULT_BEGIN` and `UNIT_TEST_RESULT_END` is replaced. The
algorithm body is not changed. Keep detailed evidence in `TestResult/`; the
source comment is a summary, not the sole test report.
