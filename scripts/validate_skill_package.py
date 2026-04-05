"""Validate the memorial-skill-builder skill package structure.

No external dependencies required — uses only Python stdlib.
Run from anywhere: python scripts/validate_skill_package.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Auto-detect skill package root (this file lives in scripts/)
SKILL_ROOT = Path(__file__).resolve().parent.parent

ERRORS: list[str] = []


def check(name: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    if not condition:
        ERRORS.append(name)


def main():
    print(f"Memorial Skill Package Validator")
    print(f"Root: {SKILL_ROOT}\n")

    # --- 1. SKILL.md structure ---
    print("=== SKILL.md ===")
    skill_md = SKILL_ROOT / "SKILL.md"
    check("SKILL.md exists", skill_md.is_file())
    if skill_md.is_file():
        content = skill_md.read_text(encoding="utf-8")
        check("Has YAML frontmatter", content.startswith("---"))
        check("Has name field", "name:" in content.split("---")[1].split("---")[0] if "---" in content else False)
        check("Has description field", "description:" in content.split("---")[1].split("---")[0] if "---" in content else False)
        check("Body has Workflow section", "## Workflow" in content)
        check("Body has References table", "## References" in content)
        check("Body has Step 0", "### 0." in content)
        check("Body has Step 5", "### 5." in content)

    # --- 2. agents/openai.yaml ---
    print("\n=== agents/ ===")
    yaml_file = SKILL_ROOT / "agents" / "openai.yaml"
    check("agents/openai.yaml exists", yaml_file.is_file())
    if yaml_file.is_file():
        yaml_content = yaml_file.read_text(encoding="utf-8")
        check("Has display_name", "display_name:" in yaml_content)
        check("Has short_description", "short_description:" in yaml_content)
        check("Has default_prompt", "default_prompt:" in yaml_content)

    # --- 3. references/ ---
    print("\n=== references/ ===")
    required_refs = [
        "spec-checklist.md",
        "safety-guardrails.md",
        "repo-map.md",
        "output-rules.md",
        "hard-boundaries.md",
        "differentiation.md",
    ]
    for ref in required_refs:
        check(f"references/{ref} exists", (SKILL_ROOT / "references" / ref).is_file())

    # --- 4. runtime/ (self-contained Python) ---
    print("\n=== runtime/ ===")
    runtime_root = SKILL_ROOT / "runtime" / "leftman_skill_system"
    check("runtime/leftman_skill_system/ exists", runtime_root.is_dir())

    required_py_files = [
        "__init__.py",
        "config.py",
        "domain/__init__.py",
        "domain/enums.py",
        "domain/models.py",
        "repositories/__init__.py",
        "repositories/interfaces.py",
        "repositories/in_memory.py",
        "services/__init__.py",
        "services/skill_service.py",
        "services/memory_service.py",
        "services/auth_service.py",
        "services/policy_service.py",
        "services/prompt_service.py",
        "services/retrieval_service.py",
        "services/conversation_service.py",
        "services/runtime_conversation_service.py",
        "services/source_service.py",
        "services/audit_service.py",
        "services/delete_export_service.py",
        "services/content_guard_service.py",
        "services/moderation_service.py",
        "api/__init__.py",
        "api/app.py",
        "api/dependencies.py",
    ]
    for py_file in required_py_files:
        check(f"runtime/leftman_skill_system/{py_file}", (runtime_root / py_file).is_file())

    # Check policies and prompts
    check("runtime/policies/default.json", (runtime_root / "policies" / "default.json").is_file())
    check("runtime/policies/high_risk_deceased.json", (runtime_root / "policies" / "high_risk_deceased.json").is_file())
    check("runtime/prompts/system.md", (runtime_root / "prompts" / "system.md").is_file())
    check("runtime/prompts/deceased_system.md", (runtime_root / "prompts" / "deceased_system.md").is_file())

    # Check no .pyc or temp files leaked
    pyc_count = len(list(runtime_root.rglob("*.pyc")))
    temp_files = len(list(runtime_root.rglob("*.2744757964976")))
    check("No .pyc files in runtime", pyc_count == 0, f"found {pyc_count}" if pyc_count else "")
    check("No temp files in runtime", temp_files == 0, f"found {temp_files}" if temp_files else "")

    # --- 5. scripts/ ---
    print("\n=== scripts/ ===")
    check("scripts/validate_skill_package.py exists", (SKILL_ROOT / "scripts" / "validate_skill_package.py").is_file())
    check("scripts/run_unit_tests.py exists", (SKILL_ROOT / "scripts" / "run_unit_tests.py").is_file())
    check("scripts/run_e2e_smoke.py exists", (SKILL_ROOT / "scripts" / "run_e2e_smoke.py").is_file())

    # --- 6. tests/ ---
    print("\n=== tests/ ===")
    check("tests/test_memory_service.py exists", (SKILL_ROOT / "tests" / "test_memory_service.py").is_file())
    check("tests/test_skill_flow.py exists", (SKILL_ROOT / "tests" / "test_skill_flow.py").is_file())

    # --- 7. No empty directories ---
    print("\n=== Clean directory check ===")
    for d in ["scripts", "tests", "references", "agents", "runtime"]:
        dir_path = SKILL_ROOT / d
        if dir_path.is_dir():
            file_count = len(list(dir_path.rglob("*")))
            check(f"{d}/ not empty", file_count > 0, f"{file_count} items")

    # --- Summary ---
    print(f"\n{'='*50}")
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} check(s) failed:")
        for e in ERRORS:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
