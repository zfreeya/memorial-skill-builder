from __future__ import annotations

from leftman_skill_system.domain.enums import MemoryStatus, SkillStatus
from leftman_skill_system.domain.models import DeleteJob, new_id, utc_now


class DeleteExportService:
    def __init__(self, delete_job_repo, skill_repo, memory_repo, source_repo, audit_repo, audit_service, auth_service=None):
        self.delete_job_repo = delete_job_repo
        self.skill_repo = skill_repo
        self.memory_repo = memory_repo
        self.source_repo = source_repo
        self.audit_repo = audit_repo
        self.audit_service = audit_service
        self.auth_service = auth_service

    def request_delete(self, *, skill_id: str, requested_by: str) -> DeleteJob:
        self._enforce_action(skill_id=skill_id, actor_id=requested_by, action="delete")
        job = DeleteJob(job_id=new_id("del"), skill_id=skill_id, requested_by=requested_by)
        self.delete_job_repo.save(job)
        self.audit_service.log("delete.requested", {"job_id": job.job_id}, skill_id=skill_id, actor_id=requested_by)
        return job

    def confirm_delete(self, *, job_id: str, actor_id: str) -> DeleteJob:
        job = self.delete_job_repo.get(job_id)
        if not job:
            raise ValueError("Delete job not found")
        skill = self.skill_repo.get(job.skill_id)
        if not skill:
            raise ValueError("Skill not found")
        self._enforce_action(skill_id=skill.skill_id, actor_id=actor_id, action="delete")

        for memory in self.memory_repo.list_by_skill(skill.skill_id):
            memory.status = MemoryStatus.DELETED
            self.memory_repo.save(memory)

        skill.status = SkillStatus.DELETED
        self.skill_repo.save(skill)
        job.status = "completed"
        job.completed_at = utc_now()
        self.delete_job_repo.save(job)
        self.audit_service.log("delete.completed", {"job_id": job.job_id}, skill_id=skill.skill_id, actor_id=actor_id)
        return job

    def export_skill(self, *, skill_id: str, actor_id: str) -> dict:
        skill = self.skill_repo.get(skill_id)
        if not skill:
            raise ValueError("Skill not found")
        self._enforce_action(skill_id=skill_id, actor_id=actor_id, action="export")
        memories = self.memory_repo.list_by_skill(skill_id)
        sources = self.source_repo.list_by_skill(skill_id)
        audits = self.audit_repo.list_by_skill(skill_id)
        snapshot = {
            "skill": {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "subject_kind": skill.subject_kind.value,
                "policy_pack": skill.policy_pack,
                "status": skill.status.value,
            },
            "memory_count": len(memories),
            "source_count": len(sources),
            "audit_count": len(audits),
            "sources": [
                {
                    "source_document_id": source.source_document_id,
                    "title": source.title,
                    "source_type": source.source_type,
                    "sensitivity": source.sensitivity,
                    "content_length": len(source.content),
                }
                for source in sources
            ],
            "memories": [
                {
                    "memory_id": memory.memory_id,
                    "memory_type": memory.memory_type.value,
                    "status": memory.status.value,
                    "content": memory.content,
                    "source_document_id": memory.source_document_id,
                }
                for memory in memories
            ],
        }
        self.audit_service.log("export.created", snapshot, skill_id=skill_id, actor_id=actor_id)
        return snapshot

    def _enforce_action(self, *, skill_id: str, actor_id: str | None, action: str):
        if self.auth_service is None:
            return
        allowed, reason = self.auth_service.enforce_policy_access(
            skill_id=skill_id,
            actor_id=actor_id,
            action=action,
        )
        if not allowed:
            raise PermissionError(reason or f"{action}_not_allowed")
