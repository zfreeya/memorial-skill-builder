from __future__ import annotations

from leftman_skill_system.domain.models import AuditLog, SafetyEvent, new_id


class AuditService:
    def __init__(self, audit_repo, safety_repo):
        self.audit_repo = audit_repo
        self.safety_repo = safety_repo

    def log(self, event_type: str, payload: dict, *, skill_id: str | None = None, actor_id: str | None = None):
        entry = AuditLog(
            audit_id=new_id("audit"),
            event_type=event_type,
            payload=payload,
            skill_id=skill_id,
            actor_id=actor_id,
        )
        self.audit_repo.save(entry)
        return entry

    def log_safety(self, severity: str, decision, reason: str, payload: dict, *, skill_id: str | None = None):
        event = SafetyEvent(
            safety_event_id=new_id("safe"),
            severity=severity,
            decision=decision,
            reason=reason,
            payload=payload,
            skill_id=skill_id,
        )
        self.safety_repo.save(event)
        return event
