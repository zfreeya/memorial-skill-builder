from fastapi import FastAPI

from leftman_skill_system.api.routes.conversations import router as conversations_router
from leftman_skill_system.api.routes.governance import router as governance_router
from leftman_skill_system.api.routes.memory import router as memory_router
from leftman_skill_system.api.routes.skills import router as skills_router
from leftman_skill_system.api.routes.sources import router as sources_router

app = FastAPI(title="LeftMan Skill System", version="0.1.0")

app.include_router(skills_router, prefix="/api/v1")
app.include_router(sources_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(governance_router, prefix="/api/v1")


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
