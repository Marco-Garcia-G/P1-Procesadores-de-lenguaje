import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
MAIN = PROJECT / "main.py"
CASES = BASE / "cases"
EXPECTED = BASE / "expected"
TMP = BASE / "tmp"
TMP.mkdir(exist_ok=True)


def run_case(case_path: Path) -> tuple[bool, str]:
    name = case_path.stem
    expected_path = EXPECTED / f"{name}.token"
    out_path = TMP / f"{name}.token"

    if not expected_path.exists():
        return False, f"{name}: expected missing"

    proc = subprocess.run(
        [sys.executable, str(MAIN), str(case_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return False, f"{name}: main.py failed ({proc.returncode})"

    generated = CASES / f"{name}.token"
    if not generated.exists():
        return False, f"{name}: generated token file missing"

    out_path.write_text(generated.read_text(encoding="utf-8"), encoding="utf-8")
    generated.unlink()

    expected = expected_path.read_text(encoding="utf-8")
    got = out_path.read_text(encoding="utf-8")
    if expected != got:
        return False, f"{name}: output differs"
    return True, f"{name}: OK"


def main() -> int:
    cases = sorted(CASES.glob("*.lava"))
    if not cases:
        print("No cases found")
        return 1

    ok_count = 0
    for case in cases:
        ok, msg = run_case(case)
        print(msg)
        if ok:
            ok_count += 1

    total = len(cases)
    print(f"\nSummary: {ok_count}/{total} passed")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
