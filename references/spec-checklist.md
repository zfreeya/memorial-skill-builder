# Spec Checklist

Use this checklist to keep the memorial skill aligned with `coding-spec.md`.

## Required Deliverables

- Keep `/docs/PRD.md` aligned to the memorial-skill business goal, user stories, requirements, acceptance criteria, risks, and version plan.
- Keep `/docs/architecture.md` aligned to the required sections: background, goals and non-goals, user scenarios, core capabilities, information architecture, key flows, module split, data flow, prompt design, memory design, retrieval, security, observability, roadmap, and comparison with the legacy implementation.
- Keep `/docs/prompt-spec.md`, `/docs/data-model.md`, `/docs/api-spec.md`, `/docs/security-compliance.md`, `/docs/testing-plan.md`, `/docs/roadmap.md`, `/docs/comparison-vs-existing.md`, and `/docs/task-breakdown.md` in sync with the latest implementation.

## Required System Capabilities

- Maintain a three-layer prompt system: system, persona, and memory prompts.
- Maintain at least four memory layers: short-term, episodic, semantic, and policy memory.
- Keep memory write, merge, update, delete, expiration, rollback, and audit rules explicit.
- Keep core entities explicit: User, Skill, Persona, Memory, Conversation, Message, RetrievalChunk, SourceDocument, ConsentRecord, AuditLog, SafetyEvent, PromptVersion, and SkillVersion.
- Keep backend services explicit: API Gateway, Auth, Skill, Prompt, Memory, Retrieval, Moderation, Audit, Export/Delete, and Admin services.
- Keep API contracts explicit: method, path, request, response, errors, idempotency, permissions, and log fields.

## Memorial-Specific Acceptance

- Treat the deceased-person scenario as the primary target, not a generic chatbot.
- Preserve provenance for every durable fact or voice instruction that can affect generated replies.
- Require consent and authorization records before enabling public or broad access.
- Support export, deletion, revocation, and audit review as first-class features.
- Prevent unsupported claims, impersonation drift, unsafe emotional dependency patterns, and prompt injection.

## Delivery Standard

- Do not describe a capability as complete unless the code path, storage boundary, and validation path exist.
- Distinguish clearly between implemented behavior, scaffolded placeholders, and planned production work.
- Prefer concrete schemas, flows, and interfaces over vague recommendations.
