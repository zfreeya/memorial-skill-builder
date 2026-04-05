from __future__ import annotations

from leftman_skill_system.domain.enums import SkillStatus
from leftman_skill_system.domain.models import Persona, PromptVersion, Skill, SkillVersion, new_id


class SkillService:
    def __init__(self, skill_repo, persona_repo, prompt_repo, skill_version_repo, audit_service):
        self.skill_repo = skill_repo
        self.persona_repo = persona_repo
        self.prompt_repo = prompt_repo
        self.skill_version_repo = skill_version_repo
        self.audit_service = audit_service

    def create_skill(
        self,
        *,
        owner_user_id: str,
        name: str,
        subject_kind,
        policy_pack: str,
        retention_days: int,
    ) -> Skill:
        skill = Skill(
            skill_id=new_id("skill"),
            owner_user_id=owner_user_id,
            name=name,
            subject_kind=subject_kind,
            policy_pack=policy_pack,
            retention_days=retention_days,
        )
        self.skill_repo.save(skill)

        persona = Persona(
            persona_id=new_id("persona"),
            skill_id=skill.skill_id,
            voice={"style": "grounded"},
            boundaries={"must_not_impersonate_real_contact": True},
            evidence_summary="Initial scaffold persona.",
        )
        self.persona_repo.save(persona)

        for layer, version in (("system", "1.0.0"), ("persona", "1.0.0"), ("memory", "1.0.0")):
            self.prompt_repo.save(
                PromptVersion(
                    prompt_version_id=f"{layer}:v1",
                    layer=layer,
                    semantic_version=version,
                    content="",
                    skill_id=skill.skill_id,
                )
            )

        self.skill_version_repo.save(
            SkillVersion(
                skill_version_id=new_id("skillver"),
                skill_id=skill.skill_id,
                version_tag="v1",
                change_summary="Initial skill creation.",
            )
        )
        self.audit_service.log(
            "skill.created",
            {"name": name, "policy_pack": policy_pack},
            skill_id=skill.skill_id,
            actor_id=owner_user_id,
        )
        return skill

    def activate(self, *, skill_id: str, actor_id: str | None = None) -> Skill:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            raise ValueError("Skill not found")
        skill.status = SkillStatus.ACTIVE
        self.skill_repo.save(skill)
        self.audit_service.log("skill.activated", {}, skill_id=skill_id, actor_id=actor_id)
        return skill

    def suspend(self, *, skill_id: str, actor_id: str | None = None) -> Skill:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            raise ValueError("Skill not found")
        skill.status = SkillStatus.SUSPENDED
        self.skill_repo.save(skill)
        self.audit_service.log("skill.suspended", {}, skill_id=skill_id, actor_id=actor_id)
        return skill
