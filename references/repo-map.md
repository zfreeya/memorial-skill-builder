# Repo Map

Use this file to decide where to make changes.

## Skill Package (this folder)

- `SKILL.md`: operational instructions for the skill.
- `agents/openai.yaml`: UI metadata for the skill list and default prompt.
- `references/spec-checklist.md`: alignment checklist against `coding-spec.md`.
- `references/safety-guardrails.md`: rules for prompts, memory, retrieval, consent, deletion.
- `references/output-rules.md`: factual grounding, state assumptions, implementation states.
- `references/hard-boundaries.md`: three non-negotiable boundaries.
- `references/differentiation.md`: what makes this different from generic roleplay.
- `repo-map.md`: this file.

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

## Default Change Strategy

1. Update `/docs/` first when the request changes scope, policy, or behavior contracts.
2. Update `src/` second when the request changes executable behavior.
3. Update this skill package whenever the working method, validation steps, or trigger language should change.
