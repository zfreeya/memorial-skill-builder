from fastapi import APIRouter, HTTPException

from leftman_skill_system.api.dependencies import container

router = APIRouter(tags=["conversations"])


@router.post("/skills/{skill_id}/conversations")
def start_conversation(skill_id: str, payload: dict):
    try:
        conversation = container.conversation_service.start_conversation(
            skill_id=skill_id,
            user_id=payload["user_id"],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"conversation_id": conversation.conversation_id, "skill_id": conversation.skill_id}


@router.post("/conversations/{conversation_id}/messages")
def respond(conversation_id: str, payload: dict):
    try:
        result = container.conversation_service.respond(
            conversation_id=conversation_id,
            user_id=payload["user_id"],
            content=payload["content"],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "conversation_id": result["conversation"].conversation_id,
        "assistant_message": {
            "role": result["assistant_message"].role,
            "content": result["assistant_message"].content,
        },
        "prompt_version_ids": result["prompt_bundle"]["prompt_version_ids"],
    }
