from enum import Enum


class SkillStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SubjectKind(str, Enum):
    PERSON = "person"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"
    BRAND = "brand"
    OTHER = "other"


class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    POLICY = "policy"


class MemoryStatus(str, Enum):
    STAGED = "staged"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELETED = "deleted"


class ConsentStatus(str, Enum):
    PENDING = "pending"
    GRANTED = "granted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class SafetyDecision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"
