from fastapi import APIRouter, HTTPException

from leftman_skill_system.api.dependencies import container

router = APIRouter(prefix="/skills/{skill_id}/sources", tags=["sources"])


@router.post("")
def create_source_document(skill_id: str, payload: dict):
    try:
        source = container.source_service.create_source_document(
            skill_id=skill_id,
            source_type=payload["source_type"],
            title=payload["title"],
            sensitivity=payload.get("sensitivity", "medium"),
            uri=payload.get("uri"),
            content=payload.get("content", ""),
            metadata=payload.get("metadata"),
            actor_id=payload.get("actor_id"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "source_document_id": source.source_document_id,
        "source_type": source.source_type,
        "sensitivity": source.sensitivity,
    }


@router.post("/import-text")
def import_text_source(skill_id: str, payload: dict):
    try:
        result = container.source_service.import_text_source(
            skill_id=skill_id,
            title=payload["title"],
            raw_text=payload["raw_text"],
            actor_id=payload.get("actor_id"),
            source_type=payload.get("source_type", "text"),
            sensitivity=payload.get("sensitivity", "medium"),
            uri=payload.get("uri"),
            auto_stage=payload.get("auto_stage", True),
            retention_days=payload.get("retention_days", container.settings.default_retention_days),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "source_document_id": result["source"].source_document_id,
        "candidate_count": len(result["candidates"]),
        "staged_memory_ids": [item.memory_id for item in result["staged_memories"]],
    }


@router.get("")
def list_source_documents(skill_id: str):
    items = container.sources.list_by_skill(skill_id)
    return {
        "items": [
            {
                "source_document_id": item.source_document_id,
                "title": item.title,
                "source_type": item.source_type,
                "sensitivity": item.sensitivity,
                "content_length": len(item.content),
            }
            for item in items
        ]
    }
