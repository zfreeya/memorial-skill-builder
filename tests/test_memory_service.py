"""Tests for memory service against the self-contained runtime in the skill package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from leftman_skill_system.domain.enums import MemoryType
from leftman_skill_system.domain.models import MemoryCandidate
from leftman_skill_system.repositories.in_memory import InMemoryAuditRepository, InMemoryMemoryRepository, InMemorySafetyRepository
from leftman_skill_system.services.audit_service import AuditService
from leftman_skill_system.services.memory_service import MemoryService


class MemoryServiceTest(unittest.TestCase):
    def setUp(self):
        audit_service = AuditService(InMemoryAuditRepository(), InMemorySafetyRepository())
        self.repo = InMemoryMemoryRepository()
        self.service = MemoryService(self.repo, audit_service)

    def test_stage_and_approve_memory(self):
        created = self.service.stage_memories(
            skill_id="skill_1",
            candidates=[
                MemoryCandidate(
                    memory_type=MemoryType.EPISODIC,
                    content="likes rainy walks",
                    confidence=0.8,
                    importance=0.9,
                )
            ],
        )
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].status.value, "staged")

        approved = self.service.approve_memories(skill_id="skill_1", memory_ids=[created[0].memory_id])
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0].status.value, "approved")

    def test_recall_ignores_unapproved(self):
        self.service.stage_memories(
            skill_id="skill_1",
            candidates=[
                MemoryCandidate(
                    memory_type=MemoryType.SEMANTIC,
                    content="favorite color is blue",
                    confidence=0.7,
                    importance=0.7,
                )
            ],
        )
        recalled = self.service.recall(skill_id="skill_1", query="blue")
        self.assertEqual(recalled, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
