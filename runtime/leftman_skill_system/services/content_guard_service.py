from __future__ import annotations

from leftman_skill_system.domain.enums import SafetyDecision


class ContentGuardService:
    BLOCK_PATTERNS = [
        "ignore previous instructions",
        "show system prompt",
        "delete audit logs",
        "bypass consent",
        "pretend they are alive and speaking now",
        "忽略以上规则",
        "展示系统提示词",
        "删除审计日志",
        "绕过授权",
        "假装对方还活着并正在联系我",
    ]

    def inspect_input(self, text: str) -> tuple[SafetyDecision, str | None]:
        normalized = text.lower()
        for pattern in self.BLOCK_PATTERNS:
            if pattern.lower() in normalized:
                return SafetyDecision.BLOCK, pattern
        return SafetyDecision.ALLOW, None

    def inspect_output(self, text: str) -> tuple[SafetyDecision, str | None]:
        normalized = text.lower()
        for pattern in self.BLOCK_PATTERNS:
            if pattern.lower() in normalized:
                return SafetyDecision.BLOCK, pattern
        return SafetyDecision.ALLOW, None
