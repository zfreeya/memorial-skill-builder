from __future__ import annotations

from pathlib import Path


class PromptService:
    def __init__(self, prompt_repo, memory_service, policy_service, prompt_dir: Path):
        self.prompt_repo = prompt_repo
        self.memory_service = memory_service
        self.policy_service = policy_service
        self.prompt_dir = prompt_dir

    def build_bundle(self, *, skill, persona, query: str, limit: int = 5) -> dict:
        policy = self.policy_service.load(skill.policy_pack)
        memories = self.memory_service.recall(skill_id=skill.skill_id, query=query, limit=limit)
        prompt_versions = {item.layer: item for item in self.prompt_repo.list_active(skill.skill_id)}
        default_files = self._default_files_for_policy(skill.policy_pack)

        system_template = prompt_versions.get("system")
        persona_template = prompt_versions.get("persona")
        memory_template = prompt_versions.get("memory")

        return {
            "policy": policy,
            "prompt_version_ids": [
                item.prompt_version_id for item in (system_template, persona_template, memory_template) if item
            ],
            "system": (system_template.content if system_template and system_template.content else self._load_default(default_files["system"])).strip(),
            "persona": (persona_template.content if persona_template and persona_template.content else self._load_default(default_files["persona"])).strip(),
            "memory": (memory_template.content if memory_template and memory_template.content else self._load_default(default_files["memory"])).strip(),
            "persona_payload": {
                "voice": persona.voice,
                "boundaries": persona.boundaries,
                "evidence_summary": persona.evidence_summary,
            },
            "memory_payload": [memory.content for memory in memories],
        }

    def _load_default(self, file_name: str) -> str:
        return (self.prompt_dir / file_name).read_text(encoding="utf-8")

    def _default_files_for_policy(self, policy_pack: str) -> dict:
        if policy_pack == "high_risk_deceased":
            return {
                "system": "deceased_system.md",
                "persona": "deceased_persona.md",
                "memory": "deceased_memory.md",
            }
        return {
            "system": "system.md",
            "persona": "persona.md",
            "memory": "memory.md",
        }
