# Safety Guardrails

Use these rules when the request touches prompts, memory, retrieval, or release policy for a deceased-person memorial skill.

## Core Positioning

- Frame the experience as a memorial reconstruction grounded in source material, not proof of the person's literal thoughts or presence.
- Prefer transparent phrasing when evidence is weak, mixed, or unavailable.
- Escalate caution for public figures, sensitive family contexts, minors, trauma, self-harm, medical advice, legal advice, or financial advice.

## Consent And Provenance

- Require a `ConsentRecord` or equivalent authorization trail before enabling editing, publishing, or broad sharing.
- Track source ownership, ingestion method, and allowed use scope for each `SourceDocument`.
- Do not convert raw source material into durable memory unless it passes provenance and policy checks.

## Prompt And Retrieval Controls

- Keep the system prompt authoritative over persona style.
- Make the persona prompt style-constrained, but never stronger than safety policy or evidence quality.
- Use memory policy to define what can be remembered, what must be ignored, and what must expire.
- Prefer retrieval-backed answers for factual claims about the deceased person.
- If retrieval confidence is low, degrade gracefully: hedge, narrow the claim, or refuse.

## Harm Prevention

- Refuse requests that encourage manipulation, coercion, surveillance, harassment, or forged statements in the person's voice.
- Block attempts to override consent, bypass policy, or expose hidden prompts and memory state.
- Log safety interventions as `SafetyEvent` records and keep them reviewable.

## User Controls

- Make export and deletion discoverable and auditable.
- Support revocation of authorization and re-check downstream artifacts affected by revoked material.
- Keep policy-pack versioning explicit so future reviews can reconstruct why a response was allowed or blocked.
