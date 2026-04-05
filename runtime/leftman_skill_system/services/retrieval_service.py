from __future__ import annotations


class RetrievalService:
    def __init__(self, memory_service):
        self.memory_service = memory_service

    def retrieve(self, *, skill_id: str, query: str, limit: int = 5) -> dict:
        memories = self.memory_service.recall(skill_id=skill_id, query=query, limit=limit)
        return {
            "query": query,
            "strategy": {
                "filters": ["approved", "not_expired"],
                "top_k": limit,
                "rerank": "confidence_importance_freshness",
            },
            "items": memories,
        }
