from __future__ import annotations


class AdminService:
    def __init__(self, audit_repo, safety_repo, delete_job_repo):
        self.audit_repo = audit_repo
        self.safety_repo = safety_repo
        self.delete_job_repo = delete_job_repo

    def get_skill_overview(self, *, skill_id: str) -> dict:
        return {
            "audit_events": len(self.audit_repo.list_by_skill(skill_id)),
            "safety_events": len(self.safety_repo.list_by_skill(skill_id)),
        }
