from __future__ import annotations

from leftman_skill_system.domain.enums import SkillStatus


class AuthService:
    def __init__(self, skill_repo, consent_repo, policy_service):
        self.skill_repo = skill_repo
        self.consent_repo = consent_repo
        self.policy_service = policy_service

    def has_active_consent(self, *, skill_id: str, actor_id: str | None, action: str) -> bool:
        for item in self.consent_repo.list_by_skill(skill_id):
            if not item.is_active():
                continue
            if self._scope_allows(scope=item.scope or {}, actor_id=actor_id, action=action):
                return True
        return False

    def enforce_policy_access(self, *, skill_id: str, actor_id: str | None, action: str) -> tuple[bool, str | None]:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            return False, "skill_not_found"
        if skill.status == SkillStatus.DELETED:
            return False, "skill_deleted"
        if action == "conversation" and skill.status != SkillStatus.ACTIVE:
            return False, "skill_not_active"
        if self.policy_service.requires_explicit_consent(skill.policy_pack):
            if not actor_id:
                return False, "actor_id_required"
            if not self.has_active_consent(skill_id=skill_id, actor_id=actor_id, action=action):
                return False, "explicit_actor_scoped_consent_required"
        return True, None

    def _scope_allows(self, *, scope: dict, actor_id: str | None, action: str) -> bool:
        allowed_actions = set(scope.get("allowed_actions", []))
        allowed_actor_ids = set(scope.get("allowed_actor_ids", []))

        if scope.get("public_memorial") is True and action == "conversation":
            return not allowed_actions or action in allowed_actions

        if scope.get("dialogue") is True and action == "conversation":
            return not allowed_actor_ids or actor_id in allowed_actor_ids

        if scope.get("manage") is True and action in {"import_source", "export", "delete"}:
            return not allowed_actor_ids or actor_id in allowed_actor_ids

        if allowed_actions and action not in allowed_actions:
            return False
        if allowed_actor_ids:
            return actor_id in allowed_actor_ids
        return False
