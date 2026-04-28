import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
MAIN = PROJECT / "main.py"
VALID = BASE / "valid"
INVALID = BASE / "invalid"


def run_valid(case_path):
    proc = subprocess.run(
        [sys.executable, str(MAIN), str(case_path)],
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        return False, f"{case_path.stem}: expected valid, got exit {proc.returncode}"
    if proc.stdout != "":
        return False, f"{case_path.stem}: expected no output for valid case"
    return True, f"{case_path.stem}: OK"


def run_invalid(case_path):
    proc = subprocess.run(
        [sys.executable, str(MAIN), str(case_path)],
        capture_output=True,
        text=True,
    )

    if proc.returncode == 0:
        return False, f"{case_path.stem}: expected invalid, got exit 0"

    if "[ERROR]" not in proc.stdout:
        return False, f"{case_path.stem}: expected semantic or syntax error output"
    return True, f"{case_path.stem}: OK"


def run_ir_sample():
    source = VALID / "07_record_function_return.lava"
    with tempfile.TemporaryDirectory() as tmp_dir:
        case_path = Path(tmp_dir) / "ir_sample.lava"
        out_path = Path(tmp_dir) / "ir_sample.ir"
        case_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

        proc = subprocess.run(
            [sys.executable, str(MAIN), "--ir", str(case_path)],
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            return False, f"ir_sample: expected IR generation, got exit {proc.returncode}"
        if proc.stdout != "":
            return False, "ir_sample: expected no output when IR generation succeeds"
        if not out_path.exists():
            return False, "ir_sample: .ir file was not generated"
        ir_text = out_path.read_text(encoding="utf-8")
        if "function make" not in ir_text or "new Point" not in ir_text:
            return False, "ir_sample: generated IR does not contain expected operations"

    return True, "ir_sample: OK"


def main():
    valid_cases = sorted(VALID.glob("*.lava"))
    invalid_cases = sorted(INVALID.glob("*.lava"))

    if not valid_cases and not invalid_cases:
        print("No cases found")
        return 1

    ok_count = 0
    total = len(valid_cases) + len(invalid_cases) + 1

    for case in valid_cases:
        ok, msg = run_valid(case)
        print(msg)
        if ok:
            ok_count += 1

    for case in invalid_cases:
        ok, msg = run_invalid(case)
        print(msg)
        if ok:
            ok_count += 1

    ok, msg = run_ir_sample()
    print(msg)
    if ok:
        ok_count += 1

    print(f"\nSummary: {ok_count}/{total} passed")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
