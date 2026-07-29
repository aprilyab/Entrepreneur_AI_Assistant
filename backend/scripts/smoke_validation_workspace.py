"""Authenticated end-to-end smoke test for the validation workspace API."""

import asyncio
import json
import uuid
import urllib.request

from sqlalchemy import delete

from app.database import async_session
from app.models.plan import Plan
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
    with urllib.request.urlopen(req) as response:
        if response.status == 204:
            return None
        return json.loads(response.read().decode())


async def create_plan(user_id: uuid.UUID) -> uuid.UUID:
    async with async_session() as session:
        plan = Plan(
            user_id=user_id,
            title="Validation workspace smoke test",
            idea="A test venture used only to exercise the live validation APIs.",
            market_analysis=(
                "## Market Overview\n"
                "- TAM is estimated at $2 billion.\n"
                "- The market has a CAGR of 12%.\n"
                "- A regulation may affect market entry."
            ),
            business_model="## Pricing\n- Single unit MSRP: $99.",
            financials=(
                "## Unit Economics\n"
                "- COGS: $25\n"
                "- CAC: $30\n"
                "- LTV: $140"
            ),
            validation_strategy=(
                "### Validation Recommendations\n"
                "1. Interview 12 target customers and require 7 to confirm the problem.\n"
                "2. Test a pricing page and require a 5% signup conversion.\n"
                "### Next Steps\n1. Start interviews."
            ),
            full_plan="Smoke test plan.",
            viability_score=60,
            status="complete",
        )
        session.add(plan)
        await session.commit()
        return plan.id


async def cleanup(user_id: uuid.UUID):
    async with async_session() as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


async def run_smoke_test():
    email = f"validation-smoke-{uuid.uuid4().hex[:10]}@example.com"
    auth = request(
        "/api/auth/register",
        method="POST",
        body={"email": email, "name": "Validation Smoke", "password": "TemporaryPass123!"},
    )
    token = auth["access_token"]
    user_id = uuid.UUID(auth["user"]["id"])

    try:
        plan_id = await create_plan(user_id)
        workspace = request(
            f"/api/plans/{plan_id}/validation-workspace/bootstrap",
            method="POST",
            token=token,
        )
        assert workspace["assumptions"], "No assumptions were created"
        assert workspace["evidence_claims"], "No evidence claims were created"
        assert workspace["experiments"], "No experiments were created"

        assumption = workspace["assumptions"][0]
        updated_assumption = request(
            f"/api/plans/{plan_id}/assumptions/{assumption['id']}",
            method="PATCH",
            token=token,
            body={"confidence": 80, "status": "validated", "source_type": "evidence"},
        )
        assert updated_assumption["confidence"] == 80
        assert updated_assumption["status"] == "validated"

        new_evidence = request(
            f"/api/plans/{plan_id}/evidence",
            method="POST",
            token=token,
            body={
                "claim": "A primary-source claim used by the smoke test.",
                "source_title": "Example primary report",
                "source_url": "https://example.com/report",
                "source_date": "2026-07-29",
                "status": "verified",
                "confidence": 90,
            },
        )
        assert new_evidence["status"] == "verified"

        experiment = workspace["experiments"][0]
        updated_experiment = request(
            f"/api/plans/{plan_id}/experiments/{experiment['id']}",
            method="PATCH",
            token=token,
            body={"status": "passed", "result": "8 of 12 interviewees confirmed the problem."},
        )
        assert updated_experiment["status"] == "passed"

        reloaded = request(f"/api/plans/{plan_id}", token=token)
        assert any(item["confidence"] == 80 for item in reloaded["assumptions"])
        assert any(item["source_url"] == "https://example.com/report" for item in reloaded["evidence_claims"])
        assert any(item["status"] == "passed" for item in reloaded["experiments"])

        print(
            json.dumps(
                {
                    "status": "passed",
                    "assumptions": len(reloaded["assumptions"]),
                    "evidence_claims": len(reloaded["evidence_claims"]),
                    "experiments": len(reloaded["experiments"]),
                    "persistence_verified": True,
                }
            )
        )
    finally:
        await cleanup(user_id)


if __name__ == "__main__":
    asyncio.run(run_smoke_test())
