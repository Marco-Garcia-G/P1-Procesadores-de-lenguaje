import os
import sys
import subprocess

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(os.path.dirname(TESTS_DIR), "main.py")
VALID_DIR = os.path.join(TESTS_DIR, "valid")
INVALID_DIR = os.path.join(TESTS_DIR, "invalid")

passed = 0
failed = 0

print("=== Tests validos (no deben producir errores) ===")
for fname in sorted(os.listdir(VALID_DIR)):
    if not fname.endswith(".lava"):
        continue
    path = os.path.join(VALID_DIR, fname)
    result = subprocess.run(
        [sys.executable, MAIN, path],
        capture_output=True, text=True
    )
    if result.returncode == 0 and not result.stdout.strip():
        print(f"  PASS  {fname}")
        passed += 1
    else:
        print(f"  FAIL  {fname}")
        if result.stdout.strip():
            print(f"        {result.stdout.strip()}")
        failed += 1

print()
print("=== Tests invalidos (deben producir errores semanticos) ===")
for fname in sorted(os.listdir(INVALID_DIR)):
    if not fname.endswith(".lava"):
        continue
    path = os.path.join(INVALID_DIR, fname)
    result = subprocess.run(
        [sys.executable, MAIN, path],
        capture_output=True, text=True
    )
    if result.returncode != 0 and "ERROR" in result.stdout:
        print(f"  PASS  {fname}: {result.stdout.strip()}")
        passed += 1
    else:
        print(f"  FAIL  {fname} (esperaba error)")
        failed += 1

print()
print(f"Resultados: {passed} pasados, {failed} fallidos")
