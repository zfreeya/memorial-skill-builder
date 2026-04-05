from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from leftman_skill_system.api.dependencies import container
from leftman_skill_system.domain.enums import MemoryType
from leftman_skill_system.domain.models import MemoryCandidate

router = APIRouter(prefix="/skills/{skill_id}/memories", tags=["memories"])


@router.post("/stage")
def stage_memories(skill_id: str, payload: dict):
    raw_candidates = payload.get("candidates", [])
    candidates: list[MemoryCandidate] = []
    for raw in raw_candidates:
        try:
            memory_type_str = raw.get("memory_type")
            if isinstance(memory_type_str, str):
                memory_type = MemoryType(memory_type_str)
            elif isinstance(memory_type_str, MemoryType):
                memory_type = memory_type_str
            else:
                raise ValueError(f"Invalid memory_type: {memory_type_str}")
            candidates.append(
                MemoryCandidate(
                    memory_type=memory_type,
                    content=str(raw.get("content", "")).strip(),
                    confidence=float(raw.get("confidence", 0.5)),
                    importance=float(raw.get("importance", 0.5)),
                    metadata=dict(raw.get("metadata", {})),
                )
            )
        except (ValueError, KeyError, TypeError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid candidate: {e}") from e
    created = container.memory_service.stage_memories(
        skill_id=skill_id,
        candidates=candidates,
        source_document_id=payload.get("source_document_id"),
        retention_days=payload.get("retention_days", container.settings.default_retention_days),
        submitted_by=payload.get("submitted_by"),
    )
    return {"created": [item.memory_id for item in created]}


@router.post("/approve")
def approve_memories(skill_id: str, payload: dict):
    approved = container.memory_service.approve_memories(
        skill_id=skill_id,
        memory_ids=payload.get("memory_ids", []),
        approved_by=payload.get("approved_by"),
    )
    return {"approved": [item.memory_id for item in approved]}


@router.get("")
def list_memories(skill_id: str, status: Optional[str] = None, memory_type: Optional[str] = None):
    items = container.memories.list_by_skill(skill_id)
    if status:
        items = [item for item in items if item.status.value == status]
    if memory_type:
        items = [item for item in items if item.memory_type.value == memory_type]
    return {
        "items": [
            {
                "memory_id": item.memory_id,
                "status": item.status.value,
                "memory_type": item.memory_type.value,
                "content": item.content,
            }
            for item in items
        ]
    }


@router.delete("/{memory_id}")
def delete_memory(skill_id: str, memory_id: str, deleted_by: Optional[str] = None):
    deleted = container.memory_service.delete_memory(skill_id=skill_id, memory_id=memory_id, deleted_by=deleted_by)
    if not deleted:
        raise HTTPException(status_code=404, detail="not_found")
    return {"memory_id": deleted.memory_id, "status": deleted.status.value}
