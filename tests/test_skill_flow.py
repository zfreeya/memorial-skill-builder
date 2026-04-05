"""Run unit tests against the self-contained runtime in the skill package.

Tests domain models, repositories, and services — no HTTP or FastAPI needed.
Run: python scripts/run_unit_tests.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add runtime to Python path
RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from leftman_skill_system.domain.enums import ConsentStatus, MemoryType, SubjectKind
from leftman_skill_system.domain.models import ConsentRecord, MemoryCandidate, new_id
from leftman_skill_system.repositories.in_memory import (
    InMemoryAuditRepository,
    InMemoryConsentRepository,
    InMemoryConversationRepository,
    InMemoryDeleteJobRepository,
    InMemoryMemoryRepository,
    InMemoryMessageRepository,
    InMemoryPersonaRepository,
    InMemoryPromptRepository,
    InMemorySafetyRepository,
    InMemorySkillRepository,
    InMemorySkillVersionRepository,
    InMemorySourceDocumentRepository,
)
from leftman_skill_system.services.audit_service import AuditService
from leftman_skill_system.services.auth_service import AuthService
from leftman_skill_system.services.runtime_conversation_service import ConversationService
from leftman_skill_system.services.delete_export_service import DeleteExportService
from leftman_skill_system.services.memory_service import MemoryService
from leftman_skill_system.services.content_guard_service import ContentGuardService
from leftman_skill_system.services.policy_service import PolicyService
from leftman_skill_system.services.prompt_service import PromptService
from leftman_skill_system.services.retrieval_service import RetrievalService
from leftman_skill_system.services.skill_service import SkillService
from leftman_skill_system.services.source_service import SourceService


BASE_DIR = RUNTIME_DIR / "leftman_skill_system"


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


class SkillFlowTest(unittest.TestCase):
    def setUp(self):
        self.audit_service = AuditService(InMemoryAuditRepository(), InMemorySafetyRepository())
        self.skills = InMemorySkillRepository()
        self.personas = InMemoryPersonaRepository()
        self.prompts = InMemoryPromptRepository()
        self.skill_versions = InMemorySkillVersionRepository()
        self.memories = InMemoryMemoryRepository()
        self.consents = InMemoryConsentRepository()
        self.conversations = InMemoryConversationRepository()
        self.messages = InMemoryMessageRepository()
        self.delete_jobs = InMemoryDeleteJobRepository()
        self.sources = InMemorySourceDocumentRepository()
        self.audits = InMemoryAuditRepository()

        self.policy_service = PolicyService(BASE_DIR / "policies")
        self.auth_service = AuthService(self.skills, self.consents, self.policy_service)
        self.memory_service = MemoryService(self.memories, self.audit_service)
        self.source_service = SourceService(self.sources, self.audit_service)
        self.retrieval_service = RetrievalService(self.memory_service)
        self.moderation_service = ContentGuardService()
        self.prompt_service = PromptService(self.prompts, self.memory_service, self.policy_service, BASE_DIR / "prompts")
        self.skill_service = SkillService(
            self.skills, self.personas, self.prompts, self.skill_versions, self.audit_service
        )
        self.conversation_service = ConversationService(
            self.conversations,
            self.messages,
            self.skills,
            self.personas,
            self.auth_service,
            self.retrieval_service,
            self.moderation_service,
            self.prompt_service,
            self.audit_service,
        )
        self.delete_export_service = DeleteExportService(
            self.delete_jobs, self.skills, self.memories, self.sources, self.audits, self.audit_service,
            consent_repo=self.consents,
        )

    def test_skill_creation_and_delete(self):
        skill = self.skill_service.create_skill(
            owner_user_id="user_1",
            name="Test Skill",
            subject_kind=SubjectKind.PERSON,
            policy_pack="default",
            retention_days=365,
        )
        self.assertEqual(skill.status.value, "draft")

        job = self.delete_export_service.request_delete(skill_id=skill.skill_id, requested_by="user_1")
        self.assertEqual(job.status, "pending")

        completed = self.delete_export_service.confirm_delete(job_id=job.job_id, actor_id="user_1")
        self.assertEqual(completed.status, "completed")
        self.assertEqual(self.skills.get(skill.skill_id).status.value, "deleted")

    def test_source_document_creation(self):
        skill = self.skill_service.create_skill(
            owner_user_id="user_1",
            name="Source Skill",
            subject_kind=SubjectKind.PERSON,
            policy_pack="default",
            retention_days=365,
        )
        source = self.source_service.create_source_document(
            skill_id=skill.skill_id,
            source_type="chat_export",
            title="wechat_2024_q1",
            sensitivity="high",
            actor_id="user_1",
        )
        self.assertEqual(source.skill_id, skill.skill_id)
        self.assertEqual(source.source_type, "chat_export")

    def test_high_risk_policy_requires_consent(self):
        skill = self.skill_service.create_skill(
            owner_user_id="user_1",
            name="Sensitive Skill",
            subject_kind=SubjectKind.PERSON,
            policy_pack="high_risk_deceased",
            retention_days=30,
        )

        # Runtime conversation service requires skill to be ACTIVE
        self.skill_service.activate(skill_id=skill.skill_id, actor_id="user_1")

        # No consent granted — should block
        with self.assertRaises(PermissionError):
            self.conversation_service.start_conversation(skill_id=skill.skill_id, user_id="user_1")

        # Grant consent without dialogue scope — still blocks conversation start
        consent_readonly = ConsentRecord(
            consent_id=new_id("consent"),
            skill_id=skill.skill_id,
            status=ConsentStatus.GRANTED,
            scope={"allowed_actor_ids": ["user_1"], "allowed_actions": ["export"]},
            granted_by="guardian_1",
        )
        self.consents.save(consent_readonly)

        with self.assertRaises(PermissionError):
            self.conversation_service.start_conversation(skill_id=skill.skill_id, user_id="user_1")

        # Grant proper consent with dialogue scope
        consent_dialogue = ConsentRecord(
            consent_id=new_id("consent"),
            skill_id=skill.skill_id,
            status=ConsentStatus.GRANTED,
            scope={
                "allowed_actor_ids": ["user_1"],
                "allowed_actions": ["conversation"],
                "dialogue": True,
            },
            granted_by="guardian_1",
        )
        self.consents.save(consent_dialogue)

        conversation = self.conversation_service.start_conversation(skill_id=skill.skill_id, user_id="user_1")

        self.memory_service.stage_memories(
            skill_id=skill.skill_id,
            candidates=[
                MemoryCandidate(
                    memory_type=MemoryType.SEMANTIC,
                    content="The person often fell silent under pressure before speaking.",
                    confidence=0.9,
                    importance=0.8,
                )
            ],
        )
        staged = self.memories.list_by_skill(skill.skill_id)
        self.memory_service.approve_memories(skill_id=skill.skill_id, memory_ids=[staged[0].memory_id])

        result = self.conversation_service.respond(
            conversation_id=conversation.conversation_id,
            user_id="user_1",
            content="how do they handle stress",
        )
        self.assertEqual(result["assistant_message"].role, "assistant")
        self.assertTrue(result["prompt_bundle"]["prompt_version_ids"])
        self.assertIn("deceased-person skill", result["prompt_bundle"]["system"])


if __name__ == "__main__":
    print("Running unit tests against skill package runtime...\n")
    unittest.main(verbosity=2)
