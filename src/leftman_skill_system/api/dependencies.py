from pathlib import Path

from leftman_skill_system.config import Settings
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
    InMemoryUserRepository,
)
from leftman_skill_system.services.audit_service import AuditService
from leftman_skill_system.services.admin_service import AdminService
from leftman_skill_system.services.auth_service import AuthService
from leftman_skill_system.services.content_guard_service import ContentGuardService
from leftman_skill_system.services.delete_export_service import DeleteExportService
from leftman_skill_system.services.memory_service import MemoryService
from leftman_skill_system.services.policy_service import PolicyService
from leftman_skill_system.services.prompt_service import PromptService
from leftman_skill_system.services.retrieval_service import RetrievalService
from leftman_skill_system.services.runtime_conversation_service import ConversationService
from leftman_skill_system.services.skill_service import SkillService
from leftman_skill_system.services.source_service import SourceService


class Container:
    def __init__(self):
        project_dir = Path(__file__).resolve().parents[3]
        base_dir = Path(__file__).resolve().parents[1]
        self.settings = Settings()
        data_dir = project_dir / self.settings.data_dir

        self.users = InMemoryUserRepository(data_dir / "users.json")
        self.skills = InMemorySkillRepository(data_dir / "skills.json")
        self.personas = InMemoryPersonaRepository(data_dir / "personas.json")
        self.memories = InMemoryMemoryRepository(data_dir / "memories.json")
        self.conversations = InMemoryConversationRepository(data_dir / "conversations.json")
        self.messages = InMemoryMessageRepository(data_dir / "messages.json")
        self.consents = InMemoryConsentRepository(data_dir / "consents.json")
        self.audits = InMemoryAuditRepository(data_dir / "audits.json")
        self.safety = InMemorySafetyRepository(data_dir / "safety_events.json")
        self.prompts = InMemoryPromptRepository(data_dir / "prompt_versions.json")
        self.skill_versions = InMemorySkillVersionRepository(data_dir / "skill_versions.json")
        self.sources = InMemorySourceDocumentRepository(data_dir / "sources.json")
        self.delete_jobs = InMemoryDeleteJobRepository(data_dir / "delete_jobs.json")

        self.audit_service = AuditService(self.audits, self.safety)
        self.policy_service = PolicyService(base_dir / "policies")
        self.auth_service = AuthService(self.skills, self.consents, self.policy_service)
        self.memory_service = MemoryService(self.memories, self.audit_service)
        self.source_service = SourceService(self.sources, self.memory_service, self.audit_service, self.auth_service)
        self.retrieval_service = RetrievalService(self.memory_service)
        self.moderation_service = ContentGuardService()
        self.prompt_service = PromptService(
            self.prompts,
            self.memory_service,
            self.policy_service,
            base_dir / "prompts",
        )
        self.skill_service = SkillService(
            self.skills,
            self.personas,
            self.prompts,
            self.skill_versions,
            self.audit_service,
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
            self.delete_jobs,
            self.skills,
            self.memories,
            self.sources,
            self.audits,
            self.audit_service,
            self.auth_service,
        )
        self.admin_service = AdminService(self.audits, self.safety, self.delete_jobs)


container = Container()
