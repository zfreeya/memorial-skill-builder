# Repo Map

Use this file to decide where to make changes.

## Skill Package (this folder)

```
memorial-skill-builder/
  SKILL.md                              — operational instructions
  references/                           — rule details, checklists, maps
  docs/                                 — supplementary design documents
  runtime/leftman_skill_system/         — self-contained Python runtime
  scripts/                              — validation and test scripts
  tests/                                — unit test files
  data/                                 — skill instances, persistence, extracted data
  AUTO_ITERATION_SPEC.md                — automated iteration rules
```

### references/

- `spec-checklist.md`: alignment checklist against `coding-spec.md`.
- `safety-guardrails.md`: rules for prompts, memory, retrieval, consent, deletion.
- `output-rules.md`: factual grounding, state assumptions, implementation states.
- `hard-boundaries.md`: three non-negotiable boundaries.
- `differentiation.md`: what makes this different from generic roleplay.
- `repo-map.md`: this file.

### scripts/

- `validate_skill_package.py`: structural validation (no dependencies).
- `run_unit_tests.py`: unit tests for domain, repos, services (no dependencies).
- `run_e2e_smoke.py`: full HTTP lifecycle smoke test (requires fastapi + uvicorn).

### runtime/leftman_skill_system/

| Module | Contents | External Deps |
|--------|----------|--------------|
| `domain/` | enums, data models | None (stdlib) |
| `repositories/` | ABC interfaces, in-memory + JSON persistence | None (stdlib) |
| `services/` | auth, memory, conversation, prompt, retrieval, audit, source, delete, moderation | None (stdlib) |
| `services/wechat_extraction/` | WeChat key extraction, DB reading, data export | psutil, ctypes (stdlib on Windows) |
| `api/` | FastAPI app, DI container, route handlers | fastapi, uvicorn |
| `prompts/` | system, persona, memory templates (6 files) | None |
| `policies/` | default.json, high_risk_deceased.json | None |

## Runtime Code (self-contained in `runtime/`)

All source code lives inside this skill package — no external repos needed.

| Path | Contents |
|------|----------|
| `runtime/leftman_skill_system/domain/` | shared enums and data models |
| `runtime/leftman_skill_system/repositories/` | repository interfaces and in-memory adapters |
| `runtime/leftman_skill_system/services/` | auth, memory, conversation, prompt, retrieval, audit, source, delete, moderation, wechat extraction |
| `runtime/leftman_skill_system/prompts/` | baseline prompt templates, including deceased-person variants |
| `runtime/leftman_skill_system/policies/` | policy packs, including the high-risk deceased policy |
| `runtime/leftman_skill_system/api/` | FastAPI app wiring, dependencies, and route handlers |

## Change Strategy

All changes are made directly within this skill package:

1. Update `references/` docs when scope, policy, or behavior contracts change.
2. Update `runtime/leftman_skill_system/` directly when executable behavior changes.
3. Update `SKILL.md` when working method, validation steps, or trigger language changes.
4. Run `scripts/validate_skill_package.py` and `scripts/run_unit_tests.py` to verify.
