from fastapi import APIRouter, HTTPException

from leftman_skill_system.api.dependencies import container
from leftman_skill_system.domain.enums import SubjectKind

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("")
def create_skill(payload: dict):
    try:
        skill = container.skill_service.create_skill(
            owner_user_id=payload["owner_user_id"],
            name=payload["name"],
            subject_kind=SubjectKind(payload["subject_kind"]),
            policy_pack=payload.get("policy_pack", container.settings.default_policy_pack),
            retention_days=payload.get("retention_days", container.settings.default_retention_days),
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"skill_id": skill.skill_id, "status": skill.status.value, "version_tag": "v1"}


@router.get("/{skill_id}")
def get_skill(skill_id: str):
    skill = container.skills.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="not_found")
    return {
        "skill_id": skill.skill_id,
        "name": skill.name,
        "status": skill.status.value,
        "policy_pack": skill.policy_pack,
    }


@router.post("/{skill_id}/activate")
def activate_skill(skill_id: str, payload: dict):
    try:
        skill = container.skill_service.activate(skill_id=skill_id, actor_id=payload.get("actor_id"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"skill_id": skill.skill_id, "status": skill.status.value}


@router.post("/{skill_id}/suspend")
def suspend_skill(skill_id: str, payload: dict):
    try:
        skill = container.skill_service.suspend(skill_id=skill_id, actor_id=payload.get("actor_id"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"skill_id": skill.skill_id, "status": skill.status.value}
