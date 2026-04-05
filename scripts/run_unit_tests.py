"""Run unit tests against the self-contained runtime in the skill package.

No external dependencies (no pip install needed) — domain, repositories, services all use stdlib.
Run: python scripts/run_unit_tests.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = SKILL_ROOT / "tests"
RUNTIME_DIR = SKILL_ROOT / "runtime"


def cleanup_runtime_bytecode() -> int:
    removed_count = 0

    for pattern in ("*.pyc", "*.pyo"):
        for artifact in RUNTIME_DIR.rglob(pattern):
            artifact.unlink()
            removed_count += 1

    for cache_dir in sorted(RUNTIME_DIR.rglob("__pycache__"), reverse=True):
        shutil.rmtree(cache_dir)
        removed_count += 1

    return removed_count


def main():
    print(f"=== Memorial Skill Builder — Unit Tests ===")
    print(f"Skill root: {SKILL_ROOT}")
    print(f"Tests dir:  {TESTS_DIR}\n")

    removed_before = cleanup_runtime_bytecode()
    if removed_before:
        print(f"Removed {removed_before} runtime bytecode artifact(s) before tests")

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS_DIR), "-v"],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )

    removed_after = cleanup_runtime_bytecode()
    if removed_after:
        print(f"Removed {removed_after} runtime bytecode artifact(s) after tests")

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode == 0:
        print("\nALL UNIT TESTS PASSED")
    else:
        print(f"\nUNIT TESTS FAILED (exit code {result.returncode})")

    sys.exit(result.returncode)



if __name__ == "__main__":
    main()
