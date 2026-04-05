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

        allowed, reason = self.auth_service.enforce_policy_access(skill_id=skill.skill_id)
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

        assistant_text = "[stub] response generated from prompt bundle"
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
