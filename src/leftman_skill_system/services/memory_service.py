from __future__ import annotations

import re

from leftman_skill_system.domain.enums import MemoryStatus
from leftman_skill_system.domain.models import Memory, default_memory_expiry, new_id, utc_now


class MemoryService:
    def __init__(self, memory_repo, audit_service):
        self.memory_repo = memory_repo
        self.audit_service = audit_service

    def stage_memories(
        self,
        *,
        skill_id: str,
        candidates: list[dict],
        source_document_id: str | None = None,
        retention_days: int = 365,
        submitted_by: str | None = None,
    ) -> list[Memory]:
        created: list[Memory] = []
        for candidate in candidates:
            memory = Memory(
                memory_id=new_id("mem"),
                skill_id=skill_id,
                memory_type=candidate["memory_type"],
                content=candidate["content"].strip(),
                confidence=float(candidate.get("confidence", 0.5)),
                importance=float(candidate.get("importance", 0.5)),
                source_document_id=source_document_id,
                valid_until=default_memory_expiry(candidate["memory_type"], retention_days),
                metadata=dict(candidate.get("metadata", {})),
            )
            self.memory_repo.save(memory)
            created.append(memory)
            self.audit_service.log(
                "memory.staged",
                {"memory_id": memory.memory_id, "memory_type": memory.memory_type.value},
                skill_id=skill_id,
                actor_id=submitted_by,
            )
        return created

    def approve_memories(self, *, skill_id: str, memory_ids: list[str], approved_by: str | None = None) -> list[Memory]:
        approved = []
        for memory_id in memory_ids:
            memory = self.memory_repo.get(memory_id)
            if not memory or memory.skill_id != skill_id:
                continue
            memory.status = MemoryStatus.APPROVED
            memory.revision += 1
            self.memory_repo.save(memory)
            approved.append(memory)
            self.audit_service.log(
                "memory.approved",
                {"memory_id": memory.memory_id},
                skill_id=skill_id,
                actor_id=approved_by,
            )
        return approved

    def delete_memory(self, *, skill_id: str, memory_id: str, deleted_by: str | None = None) -> Memory | None:
        memory = self.memory_repo.get(memory_id)
        if not memory or memory.skill_id != skill_id:
            return None
        memory.status = MemoryStatus.DELETED
        memory.revision += 1
        self.memory_repo.save(memory)
        self.audit_service.log(
            "memory.deleted",
            {"memory_id": memory.memory_id},
            skill_id=skill_id,
            actor_id=deleted_by,
        )
        return memory

    def recall(self, *, skill_id: str, query: str, limit: int = 5) -> list[Memory]:
        tokens = {token for token in re.findall(r"[\u4e00-\u9fff]+|[a-z0-9]+", query.lower()) if token}
        now = utc_now()
        approved_memories = []
        candidates = []
        for memory in self.memory_repo.list_by_skill(skill_id):
            if memory.status != MemoryStatus.APPROVED:
                continue
            if memory.valid_until and memory.valid_until <= now:
                continue
            approved_memories.append(memory)
            text = memory.content.lower()
            overlap = sum(1 for token in tokens if token in text)
            if tokens and overlap == 0:
                continue
            freshness = 1.0
            if memory.valid_until:
                total_window = max((memory.valid_until - memory.created_at).total_seconds(), 1)
                freshness = max((memory.valid_until - now).total_seconds() / total_window, 0.1)
            score = overlap + memory.confidence + memory.importance + freshness
            candidates.append((score, memory))
        if not candidates:
            for memory in approved_memories:
                freshness = 1.0
                if memory.valid_until:
                    total_window = max((memory.valid_until - memory.created_at).total_seconds(), 1)
                    freshness = max((memory.valid_until - now).total_seconds() / total_window, 0.1)
                fallback_score = memory.confidence + memory.importance + freshness
                candidates.append((fallback_score, memory))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in candidates[:limit]]
