from __future__ import annotations

import json
from pathlib import Path


class PolicyService:
    def __init__(self, policy_dir: Path):
        self.policy_dir = policy_dir

    def load(self, policy_pack: str) -> dict:
        path = self.policy_dir / f"{policy_pack}.json"
        if not path.exists():
            raise FileNotFoundError(f"Policy pack not found: {policy_pack}")
        return json.loads(path.read_text(encoding="utf-8"))

    def requires_explicit_consent(self, policy_pack: str) -> bool:
        return bool(self.load(policy_pack).get("requires_explicit_consent", False))
