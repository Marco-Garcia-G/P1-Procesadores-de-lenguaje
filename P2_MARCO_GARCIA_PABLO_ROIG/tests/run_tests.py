import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
MAIN = PROJECT / "main.py"
VALID = BASE / "valid"
INVALID = BASE / "invalid"
EXPECTED_INVALID = BASE / "expected_invalid"
TMP = BASE / "tmp"
TMP.mkdir(exist_ok=True)


def run_valid(case_path):
    proc = subprocess.run(
        [sys.executable, str(MAIN), str(case_path)],
        capture_output=True,
        text=True,
    )
    out_path = TMP / f"{case_path.stem}.valid.out"
    out_path.write_text(proc.stdout, encoding="utf-8")

    if proc.returncode != 0:
        return False, f"{case_path.stem}: expected valid, got exit {proc.returncode}"
    if proc.stdout != "":
        return False, f"{case_path.stem}: expected no output for valid case"
    return True, f"{case_path.stem}: OK"


def run_invalid(case_path):
    expected_path = EXPECTED_INVALID / f"{case_path.stem}.txt"
    if not expected_path.exists():
        return False, f"{case_path.stem}: expected output missing"

    proc = subprocess.run(
        [sys.executable, str(MAIN), str(case_path)],
        capture_output=True,
        text=True,
    )
    out_path = TMP / f"{case_path.stem}.invalid.out"
    out_path.write_text(proc.stdout, encoding="utf-8")

    if proc.returncode == 0:
        return False, f"{case_path.stem}: expected invalid, got exit 0"

    expected = expected_path.read_text(encoding="utf-8")
    if proc.stdout != expected:
        return False, f"{case_path.stem}: output differs"
    return True, f"{case_path.stem}: OK"


def main():
    valid_cases = sorted(VALID.glob("*.lava"))
    invalid_cases = sorted(INVALID.glob("*.lava"))

    if not valid_cases and not invalid_cases:
        print("No cases found")
        return 1

    ok_count = 0
    total = len(valid_cases) + len(invalid_cases)

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

    print(f"\nSummary: {ok_count}/{total} passed")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
