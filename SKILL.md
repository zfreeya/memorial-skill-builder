---
name: memorial-skill-builder
description: Use when building or auditing a memorial skill for a deceased person — including setup, consent flow, memory architecture, safety guardrails, deletion pipeline, or production readiness. Triggers include "build a memorial skill", "create a deceased-person skill", "upgrade the memorial system", "add consent flow", "fix memory architecture", "memorial skill audit", "左人 skill", "逝者对话", "已故人物 skill", "纪念 skill".
---

# Memorial Skill Builder

Build production-grade memorial skills grounded in real source material — with consent, audit, and deletion built in from day one.

## Workflow

Execute these steps in order. Do not skip.

### 0. Locate Project Root

Before anything else, identify the project root directory. This skill package lives under `~/.agents/skills/` but the codebase it operates on is a separate project repo. All `/docs/` and `src/` paths in this skill refer to the project root, not the skill package directory.

**How to find it:** Look for `docs/PRD.md`, `src/leftman_skill_system/`, `coding-spec.md`, or `pyproject.toml` in the current workspace. If the workspace is not the memorial project repo, ask the user for the correct path.

### 1. Read Current State

Read these files before changing anything:

- `SKILL.md` (this file)
- `agents/openai.yaml`
- `references/repo-map.md` — which docs and code paths to change
- `references/spec-checklist.md` — alignment with `coding-spec.md`
- `references/safety-guardrails.md` — prompt, memory, consent, deletion rules

Then state: is the current status Implemented, Scaffolded, or Planned?

### 2. Validate Skill Package Structure

- YAML frontmatter: `name` + `description` only.
- Body: concise and procedural. Details go in `references/`.
- Directories: only keep what is actually used.

### 3. Apply Memorial Domain Rules

- Deceased-person simulation = high-risk skill. Stricter boundaries than a chatbot.
- Prefer grounded reconstruction over fictional roleplay.
- Every fact or voice instruction affecting generated replies must have traceable provenance.
- Consent, authorization, audit, export, deletion are first-class citizens.

Read `references/safety-guardrails.md` and `references/hard-boundaries.md` for the full rule set.

### 4. Update Deliverables Together

Never let docs and code drift apart:

| Change type | Files to sync |
|------------|--------------|
| Scope, policy, behavior contract | `/docs/` corresponding doc — update before code |
| Executable behavior | `src/leftman_skill_system/` corresponding module |
| Working method, triggers, validation | This skill package |

`/docs/` must stay current: `PRD.md`, `architecture.md`, `prompt-spec.md`, `data-model.md`, `api-spec.md`, `security-compliance.md`, `testing-plan.md`, `roadmap.md`, `comparison-vs-existing.md`, `task-breakdown.md`.

See `references/repo-map.md` for full path reference.

### 5. Pre-Close Validation

Before closing any task, verify:

- [ ] `SKILL.md` frontmatter has only `name` and `description`
- [ ] All `references/` files exist and are internally consistent
- [ ] No empty directories in the skill package
- [ ] `agents/openai.yaml` `display_name` and `short_description` match SKILL.md
- [ ] All paths in `references/repo-map.md` resolve to existing files
- [ ] Output follows rules in `references/output-rules.md`
- [ ] Hard boundaries in `references/hard-boundaries.md` are not violated
- [ ] If code changed: run `python scripts/run_unit_tests.py` from skill root
- [ ] If available: run `python scripts/run_e2e_smoke.py` from skill root (requires fastapi/uvicorn)
- [ ] Run `python scripts/validate_skill_package.py` from skill root
- [ ] State remaining gaps between scaffold and production — do not hide them

## Self-Contained Runtime

This skill package includes a complete Python runtime under `runtime/`:

```
runtime/
  leftman_skill_system/
    domain/          — enums + data models (stdlib only)
    repositories/    — in-memory repos with JSON persistence (stdlib only)
    services/        — business logic (stdlib only)
    api/             — FastAPI HTTP layer (requires fastapi+uvicorn)
    prompts/         — prompt templates (system, persona, memory)
    policies/        — policy packs (default, high_risk_deceased)
```

**Scripts for validation:**

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scripts/validate_skill_package.py` | Structural check (files exist, no junk) | None (stdlib) |
| `scripts/run_unit_tests.py` | Domain/repo/service unit tests | None (stdlib) |
| `scripts/run_e2e_smoke.py` | Full lifecycle HTTP smoke test | fastapi, uvicorn |

All scripts auto-detect the skill root directory. Run from anywhere inside the skill package.

## References

| File | When to read |
|-----|-------------|
| `references/spec-checklist.md` | Checking alignment with `coding-spec.md` |
| `references/safety-guardrails.md` | Updating prompts, memory, retrieval, consent, deletion, abuse handling |
| `references/repo-map.md` | Deciding which docs and code paths to change |
| `references/output-rules.md` | Producing any output — factual grounding, state assumptions, implementation states |
| `references/hard-boundaries.md` | Any decision involving source, consent, or deletion |
| `references/differentiation.md` | Explaining what makes this skill different from generic roleplay |
