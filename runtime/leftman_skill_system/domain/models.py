from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from .enums import ConsentStatus, MemoryStatus, MemoryType, SafetyDecision, SkillStatus, SubjectKind


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class User:
    user_id: str
    display_name: str
    role: str = "end_user"
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Skill:
    skill_id: str
    owner_user_id: str
    name: str
    subject_kind: SubjectKind
    policy_pack: str
    retention_days: int
    status: SkillStatus = SkillStatus.DRAFT
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Persona:
    persona_id: str
    skill_id: str
    voice: dict[str, Any] = field(default_factory=dict)
    boundaries: dict[str, Any] = field(default_factory=dict)
    evidence_summary: str = ""


@dataclass
class SourceDocument:
    source_document_id: str
    skill_id: str
    source_type: str
    title: str
    uri: str | None = None
    sensitivity: str = "medium"
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Memory:
    memory_id: str
    skill_id: str
    memory_type: MemoryType
    content: str
    confidence: float
    importance: float
    status: MemoryStatus = MemoryStatus.STAGED
    source_document_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    valid_until: datetime | None = None
    revision: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    conversation_id: str
    skill_id: str
    user_id: str
    status: str = "active"
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class Message:
    message_id: str
    conversation_id: str
    role: str
    content: str
    prompt_version_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class ConsentRecord:
    consent_id: str
    skill_id: str
    status: ConsentStatus
    scope: dict[str, Any]
    granted_by: str | None = None
    expires_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)

    def is_active(self, now: datetime | None = None) -> bool:
        now = now or utc_now()
        if self.status != ConsentStatus.GRANTED:
            return False
        if self.expires_at and self.expires_at <= now:
            return False
        return True


@dataclass
class AuditLog:
    audit_id: str
    event_type: str
    payload: dict[str, Any]
    skill_id: str | None = None
    actor_id: str | None = None
    request_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class SafetyEvent:
    safety_event_id: str
    severity: str
    decision: SafetyDecision
    reason: str
    payload: dict[str, Any]
    skill_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class PromptVersion:
    prompt_version_id: str
    layer: str
    semantic_version: str
    content: str
    status: str = "active"
    skill_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class SkillVersion:
    skill_version_id: str
    skill_id: str
    version_tag: str
    change_summary: str
    snapshot_ref: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class DeleteJob:
    job_id: str
    skill_id: str
    requested_by: str
    status: str = "pending"
    requested_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None


def default_memory_expiry(memory_type: MemoryType, retention_days: int) -> datetime | None:
    if memory_type == MemoryType.SHORT_TERM:
        return utc_now() + timedelta(days=7)
    if memory_type == MemoryType.EPISODIC:
        return utc_now() + timedelta(days=min(retention_days, 365))
    return None
