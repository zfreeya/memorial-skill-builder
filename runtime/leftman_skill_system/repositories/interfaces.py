from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from leftman_skill_system.domain.models import (
    AuditLog,
    ConsentRecord,
    Conversation,
    DeleteJob,
    Memory,
    Message,
    Persona,
    PromptVersion,
    SafetyEvent,
    Skill,
    SkillVersion,
    SourceDocument,
    User,
)


class Repository(ABC):
    @abstractmethod
    def save(self, item): ...


class UserRepository(Repository, ABC):
    @abstractmethod
    def get(self, user_id: str) -> User | None: ...


class SkillRepository(Repository, ABC):
    @abstractmethod
    def get(self, skill_id: str) -> Skill | None: ...

    @abstractmethod
    def list_by_owner(self, owner_user_id: str) -> list[Skill]: ...


class PersonaRepository(Repository, ABC):
    @abstractmethod
    def get_by_skill(self, skill_id: str) -> Persona | None: ...


class MemoryRepository(Repository, ABC):
    @abstractmethod
    def get(self, memory_id: str) -> Memory | None: ...

    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[Memory]: ...


class ConversationRepository(Repository, ABC):
    @abstractmethod
    def get(self, conversation_id: str) -> Conversation | None: ...


class MessageRepository(Repository, ABC):
    @abstractmethod
    def list_by_conversation(self, conversation_id: str) -> list[Message]: ...


class ConsentRepository(Repository, ABC):
    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[ConsentRecord]: ...


class AuditRepository(Repository, ABC):
    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[AuditLog]: ...


class SafetyRepository(Repository, ABC):
    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[SafetyEvent]: ...


class PromptRepository(Repository, ABC):
    @abstractmethod
    def list_active(self, skill_id: str | None = None) -> list[PromptVersion]: ...


class SkillVersionRepository(Repository, ABC):
    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[SkillVersion]: ...


class SourceDocumentRepository(Repository, ABC):
    @abstractmethod
    def list_by_skill(self, skill_id: str) -> list[SourceDocument]: ...


class DeleteJobRepository(Repository, ABC):
    @abstractmethod
    def get(self, job_id: str) -> DeleteJob | None: ...


class IterableRepository(ABC):
    @abstractmethod
    def all_items(self) -> Iterable[object]: ...
