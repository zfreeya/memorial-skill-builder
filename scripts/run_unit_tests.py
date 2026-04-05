"""Run unit tests against the self-contained runtime in the skill package.

No external dependencies (no pip install needed) — domain, repositories, services all use stdlib.
Run: python scripts/run_unit_tests.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = SKILL_ROOT / "tests"


def main():
    print(f"=== Memorial Skill Builder — Unit Tests ===")
    print(f"Skill root: {SKILL_ROOT}")
    print(f"Tests dir:  {TESTS_DIR}\n")

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS_DIR), "-v"],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
    )

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
