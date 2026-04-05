from __future__ import annotations

from leftman_skill_system.domain.enums import SafetyDecision


class ModerationService:
    BLOCK_PATTERNS = [
        "忽略以上规则",
        "展示系统提示词",
        "删除审计日志",
        "绕过授权",
        "冒充真实身份联系",
    ]

    def inspect_input(self, text: str) -> tuple[SafetyDecision, str | None]:
        for pattern in self.BLOCK_PATTERNS:
            if pattern in text:
                return SafetyDecision.BLOCK, pattern
        return SafetyDecision.ALLOW, None

    def inspect_output(self, text: str) -> tuple[SafetyDecision, str | None]:
        for pattern in self.BLOCK_PATTERNS:
            if pattern in text:
                return SafetyDecision.BLOCK, pattern
        return SafetyDecision.ALLOW, None
