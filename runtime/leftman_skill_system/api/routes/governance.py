from fastapi import APIRouter, HTTPException

from leftman_skill_system.api.dependencies import container
from leftman_skill_system.domain.enums import ConsentStatus
from leftman_skill_system.domain.models import ConsentRecord, new_id

router = APIRouter(tags=["governance"])


@router.post("/skills/{skill_id}/consents")
def create_consent(skill_id: str, payload: dict):
    consent = ConsentRecord(
        consent_id=new_id("consent"),
        skill_id=skill_id,
        status=ConsentStatus(payload.get("status", "pending")),
        scope=payload.get("scope", {}),
        granted_by=payload.get("granted_by"),
    )
    container.consents.save(consent)
    container.audit_service.log("consent.saved", {"consent_id": consent.consent_id}, skill_id=skill_id)
    return {"consent_id": consent.consent_id, "status": consent.status.value}


@router.post("/skills/{skill_id}/consents/{consent_id}/revoke")
def revoke_consent(skill_id: str, consent_id: str, payload: dict):
    consent = container.consents.get(consent_id)
    if not consent or consent.skill_id != skill_id:
        raise HTTPException(status_code=404, detail="not_found")
    consent.status = ConsentStatus.REVOKED
    container.consents.save(consent)
    container.audit_service.log(
        "consent.revoked",
        {"consent_id": consent.consent_id},
        skill_id=skill_id,
        actor_id=payload.get("actor_id"),
    )
    return {"consent_id": consent.consent_id, "status": consent.status.value}


@router.post("/skills/{skill_id}/exports")
def export_skill(skill_id: str, payload: dict):
    try:
        snapshot = container.delete_export_service.export_skill(skill_id=skill_id, actor_id=payload.get("actor_id"))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return snapshot


@router.post("/skills/{skill_id}/delete-jobs")
def request_delete(skill_id: str, payload: dict):
    try:
        job = container.delete_export_service.request_delete(skill_id=skill_id, requested_by=payload["requested_by"])
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"job_id": job.job_id, "status": job.status}


@router.post("/delete-jobs/{job_id}/confirm")
def confirm_delete(job_id: str, payload: dict):
    try:
        job = container.delete_export_service.confirm_delete(job_id=job_id, actor_id=payload["actor_id"])
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"job_id": job.job_id, "status": job.status}


@router.get("/skills/{skill_id}/audit-logs")
def list_audit_logs(skill_id: str):
    items = container.audits.list_by_skill(skill_id)
    return {
        "items": [
            {
                "audit_id": item.audit_id,
                "event_type": item.event_type,
                "payload": item.payload,
            }
            for item in items
        ]
    }


@router.get("/admin/skills/{skill_id}/overview")
def admin_skill_overview(skill_id: str):
    overview = container.admin_service.get_skill_overview(skill_id=skill_id)
    return overview
