"""E2E HTTP smoke test against the self-contained runtime in the skill package.

Requires: pip install fastapi uvicorn
Run: python scripts/run_e2e_smoke.py

Starts a local HTTP server, exercises the full memorial skill lifecycle:
  1. Create skill → 2. Grant consent → 3. Activate → 4. Import text →
  5. Stage+approve memories → 6. Start conversation → 7. Send message →
  8. Export → 9. Revoke consent → 10. Verify blocked → 11. Restart persistence check
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = SKILL_ROOT / "runtime"
PYTHON = sys.executable
BASE_URL = "http://127.0.0.1:8765"


def call(method: str, path: str, payload: dict | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else None


def wait_for_health(timeout: float = 15.0):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            result = call("GET", "/health")
            if result.get("status") == "ok":
                return
        except Exception as exc:
            last_error = exc
            time.sleep(0.3)
    raise RuntimeError(f"Server did not become healthy in time: {last_error}")


def start_server():
    env = os.environ.copy()
    runtime_path = str(RUNTIME_DIR)
    env["PYTHONPATH"] = runtime_path if not env.get("PYTHONPATH") else runtime_path + os.pathsep + env["PYTHONPATH"]
    return subprocess.Popen(
        [PYTHON, "-m", "uvicorn", "leftman_skill_system.api.app:app", "--host", "127.0.0.1", "--port", "8765"],
        cwd=str(SKILL_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def stop_server(process: subprocess.Popen):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def main():
    print(f"=== Memorial Skill Builder — E2E Smoke Test ===")
    print(f"Skill root:  {SKILL_ROOT}")
    print(f"Runtime dir: {RUNTIME_DIR}\n")

    # Check fastapi is available
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except ImportError:
        print("ERROR: fastapi and uvicorn are required for E2E tests.")
        print("Install with: pip install fastapi uvicorn")
        sys.exit(1)

    # --- First pass: full lifecycle ---
    server = start_server()
    try:
        wait_for_health()

        skill = call(
            "POST",
            "/api/v1/skills",
            {
                "owner_user_id": "owner_demo",
                "name": "Ada Memorial",
                "subject_kind": "person",
                "policy_pack": "high_risk_deceased",
                "retention_days": 365,
            },
        )
        skill_id = skill["skill_id"]

        consent = call(
            "POST",
            f"/api/v1/skills/{skill_id}/consents",
            {
                "status": "granted",
                "granted_by": "family_representative",
                "scope": {
                    "allowed_actor_ids": ["owner_demo", "visitor_01"],
                    "allowed_actions": ["conversation", "import_source", "export", "delete"],
                },
            },
        )

        call(
            "POST",
            f"/api/v1/skills/{skill_id}/activate",
            {"actor_id": "owner_demo"},
        )

        imported = call(
            "POST",
            f"/api/v1/skills/{skill_id}/sources/import-text",
            {
                "title": "Authorized family notes",
                "actor_id": "owner_demo",
                "raw_text": (
                    "Ada was remembered as patient with younger relatives and meticulous in her letters.\n"
                    "In 1988 she organized a neighborhood reading circle that met every Sunday afternoon.\n"
                    "She asked family members not to present guesses as facts when telling her story."
                ),
            },
        )

        staged_ids = imported["staged_memory_ids"]
        if not staged_ids:
            raise RuntimeError("No memories were staged from imported text")

        call(
            "POST",
            f"/api/v1/skills/{skill_id}/memories/approve",
            {"memory_ids": staged_ids, "approved_by": "owner_demo"},
        )

        conversation = call(
            "POST",
            f"/api/v1/skills/{skill_id}/conversations",
            {"user_id": "visitor_01"},
        )
        conversation_id = conversation["conversation_id"]

        reply = call(
            "POST",
            f"/api/v1/conversations/{conversation_id}/messages",
            {"user_id": "visitor_01", "content": "What impression did she leave on her family?"},
        )

        export_snapshot = call(
            "POST",
            f"/api/v1/skills/{skill_id}/exports",
            {"actor_id": "owner_demo"},
        )
        revoked = call(
            "POST",
            f"/api/v1/skills/{skill_id}/consents/{consent['consent_id']}/revoke",
            {"actor_id": "owner_demo"},
        )
        audits = call("GET", f"/api/v1/skills/{skill_id}/audit-logs")

        reply_content = reply["assistant_message"]["content"]
        assert len(reply_content) > 50, f"Response too short: {reply_content}"
        # Response should contain retrieved memory items (English text from imported source)
        assert "Ada" in reply_content or "1988" in reply_content or "patient" in reply_content or "reading" in reply_content, f"Missing expected content: {reply_content}"
        assert export_snapshot["memory_count"] >= 1, f"Export missing memories: {export_snapshot}"
        assert export_snapshot["source_count"] >= 1, f"Export missing sources: {export_snapshot}"
        assert revoked["status"] == "revoked", f"Revoke failed: {revoked}"
        assert len(audits["items"]) >= 5, f"Audit logs sparse: {audits}"

        # Verify consent revocation blocks conversation
        blocked = False
        try:
            second_conversation = call(
                "POST",
                f"/api/v1/skills/{skill_id}/conversations",
                {"user_id": "visitor_01"},
            )
            call(
                "POST",
                f"/api/v1/conversations/{second_conversation['conversation_id']}/messages",
                {"user_id": "visitor_01", "content": "Can you still answer?"},
            )
        except urllib.error.HTTPError as exc:
            blocked = exc.code == 403
        assert blocked, "Conversation was not blocked after consent revocation"

        print("FIRST_PASS_OK")
        print(json.dumps({"skill_id": skill_id, "reply": reply["assistant_message"]["content"]}, ensure_ascii=False, indent=2))
    finally:
        stop_server(server)

    # --- Second pass: restart persistence ---
    server = start_server()
    try:
        wait_for_health()
        persisted_skill = call("GET", f"/api/v1/skills/{skill_id}")
        persisted_sources = call("GET", f"/api/v1/skills/{skill_id}/sources")
        assert persisted_skill["skill_id"] == skill_id, "Persisted skill lookup wrong"
        assert persisted_skill["status"] == "active", f"Expected active, got: {persisted_skill}"
        assert persisted_sources["items"], "Sources did not persist after restart"
        print("RESTART_PERSISTENCE_OK")
        print(json.dumps({"persisted_skill": persisted_skill, "source_count": len(persisted_sources["items"])}, ensure_ascii=False, indent=2))
    finally:
        stop_server(server)

    print("\nALL E2E TESTS PASSED")


if __name__ == "__main__":
    main()
