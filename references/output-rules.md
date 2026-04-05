# Output Rules

Every output from this skill must satisfy these requirements.

## Factual Grounding

Every durable fact or voice instruction about the deceased must have a source record (`SourceDocument` + `provenance` field). When retrieval confidence is low, degrade gracefully: hedge, narrow the claim, or refuse to answer.

## Structured Over Prompt Bloat

Do not compensate for architectural gaps by lengthening prompts. Memory must be layered, retrieval must have strategy, behavior must be traceable.

## Deletions And Audits Are Explicit

- User requests deletion → full content deletion + preserve operation metadata + cascade consent revocation check
- Safety intervention → write `SafetyEvent` record, reviewable post-hoc
- Authorization change → re-check all downstream artifacts affected

## State Assumptions

When source material is incomplete or authorization boundaries are unclear, make reasonable assumptions, list them explicitly, and continue. Only request clarification when it affects safety, compliance, or core logic.

## Three Implementation States

- `已实现 (Implemented)`: Code path, storage boundary, and validation path all exist
- `已脚手架 (Scaffolded)`: Structure exists, logic pending
- `计划中 (Planned)`: Documented, code not started

Never describe a "planned" capability as "complete".
