"""Verify that live research refresh produces clean claim-to-source evidence."""

import asyncio
import json
import time
import uuid
import urllib.request

from sqlalchemy import delete

from app.database import async_session
from app.models.plan import EvidenceClaim, Plan
from app.models.user import User


BASE_URL = "http://localhost:8000"


def request(path: str, method: str = "GET", body: dict | None = None, token: str = ""):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(req, timeout=600) as response:
        return json.loads(response.read().decode())


async def create_legacy_plan(user_id: uuid.UUID) -> uuid.UUID:
    async with async_session() as session:
        plan = Plan(
            user_id=user_id,
            title="Evidence Refresh Smoke",
            idea="A managed virtual assistant network for busy executives",
            extra_info="Premium scheduling, inbox, and administrative support.",
            market_analysis="Old market report",
            viability_score=60,
            status="complete",
        )
        session.add(plan)
        await session.flush()
        session.add_all(
            [
                EvidenceClaim(
                    plan_id=plan.id,
                    claim="Supported market size and growth claims",
                    status="unverified",
                    confidence=20,
                    notes="AI-generated claim. Add a primary source before using it.",
                ),
                EvidenceClaim(
                    plan_id=plan.id,
                    claim="Founder manually verified claim",
                    source_url="https://example.com/founder-source",
                    status="verified",
                    confidence=90,
                    notes="Founder reviewed.",
                ),
            ]
        )
        await session.commit()
        return plan.id


async def cleanup(user_id: uuid.UUID):
    async with async_session() as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


async def main():
    email = f"research-refresh-{uuid.uuid4().hex[:10]}@example.com"
    auth = request(
        "/api/auth/register",
        method="POST",
        body={"email": email, "name": "Research Smoke", "password": "TemporaryPass123!"},
    )
    token = auth["access_token"]
    user_id = uuid.UUID(auth["user"]["id"])
    try:
        plan_id = await create_legacy_plan(user_id)
        started = time.monotonic()
        plan = request(
            f"/api/plans/{plan_id}/research/refresh",
            method="POST",
            token=token,
        )
        evidence = plan["evidence_claims"]
        claims = [item["claim"] for item in evidence]
        linked = [item for item in evidence if item.get("source_url")]
        if "Supported market size and growth claims" in claims:
            raise AssertionError("Stale generated heading was not removed.")
        if "Founder manually verified claim" not in claims:
            raise AssertionError("Manually verified evidence was not preserved.")
        if len(evidence) > 13:
            raise AssertionError(f"Evidence refresh produced too many rows: {len(evidence)}")
        if len(linked) < 4:
            raise AssertionError("Too few refreshed claims have attached source URLs.")
        if any("Source Index" in claim or claim.startswith("[S") for claim in claims):
            raise AssertionError("Source-index content leaked into evidence claims.")
        if any(
            domain in (item.get("source_url") or "")
            for item in linked
            for domain in ("linkedin.com", "instagram.com")
        ):
            raise AssertionError("Low-signal social result leaked into sourced evidence.")
        print(
            json.dumps(
                {
                    "status": "passed",
                    "evidence_rows": len(evidence),
                    "linked_claims": len(linked),
                    "verified_preserved": True,
                    "stale_generated_removed": True,
                    "elapsed_seconds": round(time.monotonic() - started, 1),
                }
            )
        )
    finally:
        await cleanup(user_id)


if __name__ == "__main__":
    asyncio.run(main())
