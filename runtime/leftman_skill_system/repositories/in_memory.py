from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, get_args, get_origin

from leftman_skill_system.domain.enums import ConsentStatus, MemoryStatus, MemoryType, SafetyDecision, SkillStatus, SubjectKind
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
from leftman_skill_system.repositories.interfaces import (
    AuditRepository,
    ConsentRepository,
    ConversationRepository,
    DeleteJobRepository,
    IterableRepository,
    MemoryRepository,
    MessageRepository,
    PersonaRepository,
    PromptRepository,
    SafetyRepository,
    SkillRepository,
    SkillVersionRepository,
    SourceDocumentRepository,
    UserRepository,
)


def _encode_value(value: Any):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {item.name: _encode_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, list):
        return [_encode_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _encode_value(item) for key, item in value.items()}
    return value


def _decode_value(value: Any, expected_type: Any):
    if value is None:
        return None

    origin = get_origin(expected_type)
    if origin is list:
        inner_type = get_args(expected_type)[0] if get_args(expected_type) else Any
        return [_decode_value(item, inner_type) for item in value]
    if origin is dict:
        args = get_args(expected_type)
        value_type = args[1] if len(args) == 2 else Any
        return {key: _decode_value(item, value_type) for key, item in value.items()}
    if origin is tuple:
        args = get_args(expected_type)
        return tuple(_decode_value(item, args[0] if args else Any) for item in value)
    if origin is not None:
        for option in get_args(expected_type):
            if option is type(None):
                continue
            try:
                return _decode_value(value, option)
            except Exception:
                continue
        return value

    if expected_type is Any:
        return value
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)
    if expected_type is datetime:
        return datetime.fromisoformat(value)
    return value


def _parse_datetime(value):
    return datetime.fromisoformat(value) if value is not None else None


FIELD_DECODERS = {
    User: {
        "created_at": _parse_datetime,
    },
    Skill: {
        "subject_kind": SubjectKind,
        "status": SkillStatus,
        "created_at": _parse_datetime,
        "updated_at": _parse_datetime,
    },
    Persona: {},
    SourceDocument: {
        "created_at": _parse_datetime,
    },
    Memory: {
        "memory_type": MemoryType,
        "status": MemoryStatus,
        "created_at": _parse_datetime,
        "valid_until": _parse_datetime,
    },
    Conversation: {
        "created_at": _parse_datetime,
    },
    Message: {
        "created_at": _parse_datetime,
    },
    ConsentRecord: {
        "status": ConsentStatus,
        "expires_at": _parse_datetime,
        "created_at": _parse_datetime,
    },
    AuditLog: {
        "created_at": _parse_datetime,
    },
    SafetyEvent: {
        "decision": SafetyDecision,
        "created_at": _parse_datetime,
    },
    PromptVersion: {
        "created_at": _parse_datetime,
    },
    SkillVersion: {
        "created_at": _parse_datetime,
    },
    DeleteJob: {
        "requested_at": _parse_datetime,
        "completed_at": _parse_datetime,
    },
}


def _deserialize_dataclass(model_cls, payload: dict):
    kwargs = {}
    decoders = FIELD_DECODERS.get(model_cls, {})
    for item in fields(model_cls):
        if item.name not in payload:
            continue
        value = payload[item.name]
        decoder = decoders.get(item.name)
        kwargs[item.name] = decoder(value) if decoder else value
    return model_cls(**kwargs)


class _BaseInMemoryRepo(IterableRepository):
    def __init__(self, key_field: str, model_cls=None, storage_path: Path | None = None):
        self.key_field = key_field
        self.model_cls = model_cls
        self.storage_path = Path(storage_path) if storage_path else None
        self._items: dict[str, object] = {}
        if self.storage_path:
            self._load()

    def save(self, item):
        self._items[getattr(item, self.key_field)] = item
        if self.storage_path:
            self._flush()
        return item

    def get(self, key: str):
        return self._items.get(key)

    def all_items(self) -> Iterable[object]:
        return self._items.values()

    def _flush(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [_encode_value(item) for item in self._items.values()]
        self.storage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self):
        if not self.storage_path.exists():
            return
        raw_items = json.loads(self.storage_path.read_text(encoding="utf-8"))
        for payload in raw_items:
            item = _deserialize_dataclass(self.model_cls, payload) if self.model_cls else payload
            self._items[getattr(item, self.key_field)] = item


class InMemoryUserRepository(_BaseInMemoryRepo, UserRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("user_id", User, storage_path)


class InMemorySkillRepository(_BaseInMemoryRepo, SkillRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("skill_id", Skill, storage_path)

    def list_by_owner(self, owner_user_id: str) -> list:
        return [item for item in self._items.values() if item.owner_user_id == owner_user_id]


class InMemoryPersonaRepository(_BaseInMemoryRepo, PersonaRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("persona_id", Persona, storage_path)

    def get_by_skill(self, skill_id: str):
        for item in self._items.values():
            if item.skill_id == skill_id:
                return item
        return None


class InMemoryMemoryRepository(_BaseInMemoryRepo, MemoryRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("memory_id", Memory, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemoryConversationRepository(_BaseInMemoryRepo, ConversationRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("conversation_id", Conversation, storage_path)


class InMemoryMessageRepository(_BaseInMemoryRepo, MessageRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("message_id", Message, storage_path)

    def list_by_conversation(self, conversation_id: str) -> list:
        items = [item for item in self._items.values() if item.conversation_id == conversation_id]
        return sorted(items, key=lambda item: item.created_at)


class InMemoryConsentRepository(_BaseInMemoryRepo, ConsentRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("consent_id", ConsentRecord, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemoryAuditRepository(_BaseInMemoryRepo, AuditRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("audit_id", AuditLog, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemorySafetyRepository(_BaseInMemoryRepo, SafetyRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("safety_event_id", SafetyEvent, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemoryPromptRepository(_BaseInMemoryRepo, PromptRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("prompt_version_id", PromptVersion, storage_path)

    def list_active(self, skill_id: str | None = None) -> list:
        items = [item for item in self._items.values() if item.status == "active"]
        if skill_id is None:
            return items
        return [item for item in items if item.skill_id in (None, skill_id)]


class InMemorySkillVersionRepository(_BaseInMemoryRepo, SkillVersionRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("skill_version_id", SkillVersion, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemorySourceDocumentRepository(_BaseInMemoryRepo, SourceDocumentRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("source_document_id", SourceDocument, storage_path)

    def list_by_skill(self, skill_id: str) -> list:
        return [item for item in self._items.values() if item.skill_id == skill_id]


class InMemoryDeleteJobRepository(_BaseInMemoryRepo, DeleteJobRepository):
    def __init__(self, storage_path: Path | None = None):
        super().__init__("job_id", DeleteJob, storage_path)
