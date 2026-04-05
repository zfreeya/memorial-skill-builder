# Repo Map

Use this file to decide where to make changes.

## Skill Package (this folder)

```
memorial-skill-builder/
  SKILL.md                              — operational instructions
  agents/openai.yaml                    — UI metadata and default prompt
  references/                           — rule details, checklists, maps
  runtime/leftman_skill_system/         — self-contained Python runtime
  scripts/                              — validation and test scripts
  tests/                                — unit test files
  data/runtime/                         — JSON persistence (auto-created at runtime)
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
| `api/` | FastAPI app, DI container, route handlers | fastapi, uvicorn |
| `prompts/` | system, persona, memory templates (6 files) | None |
| `policies/` | default.json, high_risk_deceased.json | None |

## Product And Design Docs (project root `/docs/`)

- `docs/PRD.md`: product intent, user stories, scope, acceptance, and milestone framing.
- `docs/architecture.md`: service split, flows, data movement, risk boundaries, deployment, and observability.
- `docs/prompt-spec.md`: system, persona, and memory prompt rules plus versioning and injection defense.
- `docs/data-model.md`: entities, fields, lifecycle, and relationships.
- `docs/api-spec.md`: endpoint contracts and governance operations.
- `docs/security-compliance.md`: consent, retention, deletion, access control, and misuse handling.
- `docs/testing-plan.md`: unit, integration, regression, red-team, and acceptance strategy.
- `docs/roadmap.md`: milestone plan from scaffold to production.
- `docs/comparison-vs-existing.md`: what is retained, rewritten, added, or removed from the legacy design.
- `docs/task-breakdown.md`: execution order, deliverables, rollback, and acceptance checklist.

## Current Codebase (project root `/src/`)

- `src/leftman_skill_system/domain`: shared enums and data models.
- `src/leftman_skill_system/repositories`: repository interfaces and in-memory adapters.
- `src/leftman_skill_system/services`: business services for auth, prompts, memory, moderation, retrieval, audit, exports, source handling, and admin controls.
- `src/leftman_skill_system/prompts`: baseline prompt templates, including deceased-person variants.
- `src/leftman_skill_system/policies`: policy packs, including the high-risk deceased policy.
- `src/leftman_skill_system/api`: app wiring, dependencies, and route handlers.
- `tests`: behavioral checks for core flows.

**Note:** `runtime/leftman_skill_system/` in this skill package is a copy of the project's `src/leftman_skill_system/`. When making code changes, update the project repo first, then re-sync to the skill package.

## Default Change Strategy

1. Update `/docs/` first when the request changes scope, policy, or behavior contracts.
2. Update `src/` in the project repo second when the request changes executable behavior.
3. Sync `runtime/` in this skill package from the project repo after code changes.
4. Update this skill package whenever the working method, validation steps, or trigger language should change.
