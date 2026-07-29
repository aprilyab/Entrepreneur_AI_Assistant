"""Exercise cancellation and resume against a real background generation job."""

import asyncio
import json
import time
import uuid
import urllib.request

from sqlalchemy import delete

from app.database import async_session
from app.models.user import User


BASE_URL = "http://localhost:8000"


def request(path: str, method: str = "GET", body: dict | None = None, token: str = ""):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=payload,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode())


async def cleanup(user_id: uuid.UUID):
    async with async_session() as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


def wait_for(token: str, plan_id: str, statuses: set[str], timeout: int = 240):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = request(f"/api/plans/{plan_id}/generation", token=token)
        if job["status"] in statuses:
            return job
        time.sleep(0.75)
    raise TimeoutError(f"Job did not reach {statuses} within {timeout} seconds.")


async def main():
    email = f"cancel-resume-{uuid.uuid4().hex[:10]}@example.com"
    auth = request(
        "/api/auth/register",
        method="POST",
        body={"email": email, "name": "Cancel Resume Smoke", "password": "TemporaryPass123!"},
    )
    token = auth["access_token"]
    user_id = uuid.UUID(auth["user"]["id"])
    try:
        started = request(
            "/api/plans",
            method="POST",
            token=token,
            body={
                "title": "Cancellation Test",
                "idea": "A scheduling and payment tool for independent language tutors.",
                "extra_info": "Testing durable workflow cancellation and resume.",
            },
        )
        plan_id = started["id"]
        running = wait_for(token, plan_id, {"running"})
        cancelled_request = request(
            f"/api/plans/{plan_id}/generation/cancel",
            method="POST",
            token=token,
        )
        assert cancelled_request["cancel_requested"] is True
        cancelled = wait_for(token, plan_id, {"cancelled"})
        saved_progress = cancelled["progress"]

        resumed = request(
            f"/api/plans/{plan_id}/generation/resume",
            method="POST",
            token=token,
        )
        assert resumed["status"] == "queued"
        completed = wait_for(token, plan_id, {"completed", "failed"}, timeout=600)
        assert completed["status"] == "completed", completed
        plan = request(f"/api/plans/{plan_id}", token=token)
        assert plan["status"] == "complete"
        assert completed["attempts"] >= 2
        print(
            json.dumps(
                {
                    "status": "passed",
                    "cancelled_at_progress": saved_progress,
                    "resumed_from_saved_state": True,
                    "attempts": completed["attempts"],
                    "final_progress": completed["progress"],
                }
            )
        )
    finally:
        await cleanup(user_id)


if __name__ == "__main__":
    asyncio.run(main())
