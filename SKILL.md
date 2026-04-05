---
name: memorial-skill-builder
description: "This skill should be used when building or auditing a memorial skill for a deceased person — including setup, consent flow, memory architecture, safety guardrails, deletion pipeline, or production readiness. Triggers include: 'build a memorial skill', 'create a deceased-person skill', 'upgrade the memorial system', 'add consent flow', 'fix memory architecture', 'memorial skill audit', '\u5de6\u4eba skill', '\u901d\u8005\u5bf9\u8bdd', '\u5df2\u6545\u4eba\u7269 skill', '\u7eaa\u5ff5 skill'."
---

# Memorial Skill Builder

Build production-grade memorial skills grounded in real source material, with consent, audit, and deletion built in from day one.

## Workflow

Execute these steps in order. Do not skip.

### 1. Read Current State

Read these files before changing anything:

- `references/repo-map.md` — which docs and code paths to change
- `references/safety-guardrails.md` — prompt, memory, consent, deletion rules
- `references/hard-boundaries.md` — three non-negotiable boundaries
- `references/spec-checklist.md` — alignment with upstream design spec
- `references/output-rules.md` — output quality rules
- `references/differentiation.md` — what makes this different from generic roleplay

State the current status: **Implemented**, **Scaffolded**, or **Planned**.

### 2. Validate Skill Package Structure

- YAML frontmatter: `name` + `description` only.
- Body: concise and procedural. Details go in `references/`.
- Directories: only keep what is actually used.
- No empty directories.

### 3. Apply Memorial Domain Rules

- Deceased-person simulation = high-risk skill. Apply stricter boundaries than a chatbot.
- Prefer grounded reconstruction over fictional roleplay.
- Trace provenance for every fact or voice instruction affecting generated replies.
- Treat consent, authorization, audit, export, and deletion as first-class citizens.

### 4. Update Deliverables Together

Never let docs and code drift apart:

| Change type | Files to sync |
|------------|--------------|
| Scope, policy, behavior contract | Update design docs in companion repo `/docs/` before code |
| Executable behavior | Update `src/` in companion repo, then sync to `runtime/` |
| Working method, triggers, validation | Update this skill package |

### 5. Pre-Close Validation

Before closing any task, verify:

- [ ] `SKILL.md` frontmatter has only `name` and `description`
- [ ] All `references/` files exist and are internally consistent
- [ ] No empty directories in the skill package
- [ ] All paths in `references/repo-map.md` resolve to existing files
- [ ] Output follows rules in `references/output-rules.md`
- [ ] Hard boundaries in `references/hard-boundaries.md` are not violated
- [ ] If code changed: run `python scripts/run_unit_tests.py` from skill root
- [ ] If available: run `python scripts/run_e2e_smoke.py` from skill root
- [ ] Run `python scripts/validate_skill_package.py` from skill root
- [ ] State remaining gaps between scaffold and production

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

## Validation Scripts

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scripts/validate_skill_package.py` | Structural check (files exist, no junk) | None (stdlib) |
| `scripts/run_unit_tests.py` | Domain/repo/service unit tests | None (stdlib) |
| `scripts/run_e2e_smoke.py` | Full lifecycle HTTP smoke test | fastapi, uvicorn |

All scripts auto-detect the skill root directory. Run from anywhere inside the skill package.

## References

| File | When to read |
|-----|-------------|
| `references/spec-checklist.md` | Checking alignment with upstream design spec |
| `references/safety-guardrails.md` | Updating prompts, memory, retrieval, consent, deletion, abuse handling |
| `references/repo-map.md` | Deciding which docs and code paths to change |
| `references/output-rules.md` | Producing any output — factual grounding, state assumptions, implementation states |
| `references/hard-boundaries.md` | Any decision involving source, consent, or deletion |
| `references/differentiation.md` | Explaining what makes this skill different from generic roleplay |
