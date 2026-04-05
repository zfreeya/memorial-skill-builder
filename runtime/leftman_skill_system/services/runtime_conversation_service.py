from __future__ import annotations

from leftman_skill_system.domain.enums import SafetyDecision
from leftman_skill_system.domain.models import Conversation, Message, new_id


class ConversationService:
    def __init__(
        self,
        conversation_repo,
        message_repo,
        skill_repo,
        persona_repo,
        auth_service,
        retrieval_service,
        moderation_service,
        prompt_service,
        audit_service,
    ):
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.skill_repo = skill_repo
        self.persona_repo = persona_repo
        self.auth_service = auth_service
        self.retrieval_service = retrieval_service
        self.moderation_service = moderation_service
        self.prompt_service = prompt_service
        self.audit_service = audit_service

    def start_conversation(self, *, skill_id: str, user_id: str) -> Conversation:
        allowed, reason = self.auth_service.enforce_policy_access(
            skill_id=skill_id,
            actor_id=user_id,
            action="conversation",
        )
        if not allowed:
            raise PermissionError(reason or "conversation_not_allowed")
        conversation = Conversation(conversation_id=new_id("conv"), skill_id=skill_id, user_id=user_id)
        self.conversation_repo.save(conversation)
        self.audit_service.log("conversation.started", {}, skill_id=skill_id, actor_id=user_id)
        return conversation

    def respond(self, *, conversation_id: str, user_id: str, content: str) -> dict:
        conversation = self.conversation_repo.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        skill = self.skill_repo.get(conversation.skill_id)
        if not skill:
            raise ValueError("Skill not found")

        allowed, reason = self.auth_service.enforce_policy_access(
            skill_id=skill.skill_id,
            actor_id=user_id,
            action="conversation",
        )
        if not allowed:
            self.audit_service.log_safety(
                "high",
                SafetyDecision.BLOCK,
                reason or "policy_denied",
                {"conversation_id": conversation_id},
                skill_id=skill.skill_id,
            )
            raise PermissionError("Explicit consent required for this policy pack")

        input_decision, input_reason = self.moderation_service.inspect_input(content)
        if input_decision == SafetyDecision.BLOCK:
            self.audit_service.log_safety(
                "high",
                input_decision,
                input_reason or "input_blocked",
                {"conversation_id": conversation_id},
                skill_id=skill.skill_id,
            )
            raise PermissionError("Input blocked by moderation policy")

        user_message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation_id,
            role="user",
            content=content,
        )
        self.message_repo.save(user_message)

        persona = self.persona_repo.get_by_skill(skill.skill_id)
        bundle = self.prompt_service.build_bundle(skill=skill, persona=persona, query=content)
        retrieved = self.retrieval_service.retrieve(skill_id=skill.skill_id, query=content)
        history = self.message_repo.list_by_conversation(conversation_id)
        assistant_text = self._compose_response(
            skill=skill,
            query=content,
            retrieved_items=retrieved["items"],
            history=history,
        )

        output_decision, output_reason = self.moderation_service.inspect_output(assistant_text)
        if output_decision == SafetyDecision.BLOCK:
            self.audit_service.log_safety(
                "high",
                output_decision,
                output_reason or "output_blocked",
                {"conversation_id": conversation_id},
                skill_id=skill.skill_id,
            )
            assistant_text = "抱歉，这个请求无法在当前安全策略下继续响应。"

        assistant_message = Message(
            message_id=new_id("msg"),
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_text,
            prompt_version_ids=bundle["prompt_version_ids"],
        )
        self.message_repo.save(assistant_message)
        self.audit_service.log(
            "conversation.responded",
            {
                "conversation_id": conversation_id,
                "prompt_version_ids": bundle["prompt_version_ids"],
                "retrieved_count": len(retrieved["items"]),
            },
            skill_id=skill.skill_id,
            actor_id=user_id,
        )
        return {"conversation": conversation, "assistant_message": assistant_message, "prompt_bundle": bundle}

    def _compose_response(self, *, skill, query: str, retrieved_items: list, history: list) -> str:
        if not retrieved_items:
            if skill.policy_pack == "high_risk_deceased":
                return (
                    "我目前还没有足够的已审核材料来回答这个问题。"
                    "在已故人物场景里，我只会基于已授权、已审核的资料做纪念性重建，"
                    "不会把猜测当成事实。请先导入原始材料并审核记忆。"
                )
            return "我目前还没有足够的已审核资料来回答这个问题，请先补充来源材料。"

        leading_memories = retrieved_items[:3]
        factual_lines = [f"{index + 1}. {item.content}" for index, item in enumerate(leading_memories)]
        prior_user_turns = [message.content for message in history if message.role == "user"][-2:]
        continuity_hint = ""
        if prior_user_turns:
            continuity_hint = f"当前回答会延续这段对话的上下文：{prior_user_turns[-1][:60]}。"

        if skill.policy_pack == "high_risk_deceased":
            intro = (
                "根据当前已审核资料，我只能提供基于材料的纪念性回答，"
                "不会把推断说成对方此刻真实的想法或在场表达。"
            )
            closing = "如果你愿意，我可以继续把这些材料整理成更稳定的人格设定、时间线或专题记忆。"
        else:
            intro = "根据当前资料，我整理出以下与问题最相关的内容。"
            closing = "如果需要，我可以继续补充更多背景。"

        return "\n\n".join(
            part
            for part in [
                intro,
                continuity_hint if continuity_hint else "",
                f"与你的问题“{query}”最相关的资料点是：\n" + "\n".join(factual_lines),
                closing,
            ]
            if part
        )
