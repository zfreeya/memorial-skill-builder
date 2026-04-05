from __future__ import annotations

import re

from leftman_skill_system.domain.enums import MemoryType
from leftman_skill_system.domain.models import SourceDocument, new_id


class SourceService:
    def __init__(self, source_repo, memory_service=None, audit_service=None, auth_service=None):
        if audit_service is None:
            audit_service = memory_service
            memory_service = None
        self.source_repo = source_repo
        self.memory_service = memory_service
        self.audit_service = audit_service
        self.auth_service = auth_service

    def create_source_document(
        self,
        *,
        skill_id: str,
        source_type: str,
        title: str,
        sensitivity: str = "medium",
        uri: str | None = None,
        content: str = "",
        metadata: dict | None = None,
        actor_id: str | None = None,
    ) -> SourceDocument:
        self._enforce_import_access(skill_id=skill_id, actor_id=actor_id)
        source = SourceDocument(
            source_document_id=new_id("src"),
            skill_id=skill_id,
            source_type=source_type,
            title=title,
            uri=uri,
            sensitivity=sensitivity,
            content=content.strip(),
            metadata=dict(metadata or {}),
        )
        self.source_repo.save(source)
        self.audit_service.log(
            "source_document.created",
            {
                "source_document_id": source.source_document_id,
                "source_type": source.source_type,
                "sensitivity": source.sensitivity,
                "content_length": len(source.content),
            },
            skill_id=skill_id,
            actor_id=actor_id,
        )
        return source

    def import_text_source(
        self,
        *,
        skill_id: str,
        title: str,
        raw_text: str,
        actor_id: str | None = None,
        source_type: str = "text",
        sensitivity: str = "medium",
        uri: str | None = None,
        auto_stage: bool = True,
        retention_days: int = 365,
    ) -> dict:
        source = self.create_source_document(
            skill_id=skill_id,
            source_type=source_type,
            title=title,
            sensitivity=sensitivity,
            uri=uri,
            content=raw_text,
            metadata={"import_mode": "raw_text"},
            actor_id=actor_id,
        )
        candidates = self.extract_memory_candidates(raw_text)
        staged = []
        if auto_stage and candidates:
            if self.memory_service is None:
                raise ValueError("Memory service is required for auto-stage imports")
            staged = self.memory_service.stage_memories(
                skill_id=skill_id,
                candidates=candidates,
                source_document_id=source.source_document_id,
                retention_days=retention_days,
                submitted_by=actor_id,
            )
        self.audit_service.log(
            "source_document.imported_text",
            {
                "source_document_id": source.source_document_id,
                "candidate_count": len(candidates),
                "staged_count": len(staged),
            },
            skill_id=skill_id,
            actor_id=actor_id,
        )
        return {"source": source, "candidates": candidates, "staged_memories": staged}

    def _enforce_import_access(self, *, skill_id: str, actor_id: str | None):
        if self.auth_service is None:
            return
        allowed, reason = self.auth_service.enforce_policy_access(
            skill_id=skill_id,
            actor_id=actor_id,
            action="import_source",
        )
        if not allowed:
            raise PermissionError(reason or "import_source_not_allowed")

    def extract_memory_candidates(self, raw_text: str, limit: int = 12) -> list[dict]:
        seen: set[str] = set()
        candidates: list[dict] = []
        fragments = re.split(r"[\r\n]+|[。！？!?；;]", raw_text)
        for fragment in fragments:
            cleaned = re.sub(r"^[\-\*\d\.\)\(、\s]+", "", fragment).strip()
            if len(cleaned) < 8:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            memory_type = self._guess_memory_type(cleaned)
            candidates.append(
                {
                    "memory_type": memory_type,
                    "content": cleaned,
                    "confidence": 0.82 if memory_type == MemoryType.SEMANTIC else 0.76,
                    "importance": 0.7 if memory_type == MemoryType.POLICY else 0.8,
                    "metadata": {"extracted_from": "text_import"},
                }
            )
            if len(candidates) >= limit:
                break
        return candidates

    def _guess_memory_type(self, text: str) -> MemoryType:
        lowered = text.lower()
        if any(keyword in text for keyword in ("必须", "不要", "不得", "仅可", "需经授权")):
            return MemoryType.POLICY
        if any(token in lowered for token in ("born", "died", "married", "published")):
            return MemoryType.EPISODIC
        if re.search(r"\b(19|20)\d{2}\b", text):
            return MemoryType.EPISODIC
        return MemoryType.SEMANTIC
