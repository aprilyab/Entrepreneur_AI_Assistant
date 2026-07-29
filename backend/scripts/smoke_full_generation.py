"""Run one real authenticated business-plan generation through the live API."""

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
    with urllib.request.urlopen(req, timeout=600) as response:
        return json.loads(response.read().decode())


async def cleanup(user_id: uuid.UUID):
    async with async_session() as session:
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


async def main():
    email = f"full-generation-{uuid.uuid4().hex[:10]}@example.com"
    auth = request(
        "/api/auth/register",
        method="POST",
        body={"email": email, "name": "Generation Smoke", "password": "TemporaryPass123!"},
    )
    token = auth["access_token"]
    user_id = uuid.UUID(auth["user"]["id"])
    try:
        started = request(
            "/api/plans",
            method="POST",
            token=token,
            body={
                "title": "Dentist Reminder Test",
                "idea": (
                    "A subscription appointment-reminder service for independent dental "
                    "clinics in Addis Ababa that reduces patient no-shows through SMS."
                ),
                "extra_info": "Founder budget is $5,000 and the first target is 20 clinics.",
            },
        )
        plan_id = started["id"]
        observed_stages = []
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            job = request(f"/api/plans/{plan_id}/generation", token=token)
            if not observed_stages or observed_stages[-1] != job["current_stage"]:
                observed_stages.append(job["current_stage"])
            if job["status"] == "completed":
                break
            if job["status"] in ("failed", "cancelled"):
                raise AssertionError(
                    f"Generation ended unexpectedly: {job['status']} / {job.get('error_type')}"
                )
            time.sleep(1)
        else:
            raise TimeoutError("Background generation did not finish within 10 minutes.")

        plan = request(f"/api/plans/{plan_id}", token=token)
        required_sections = [
            "market_analysis",
            "business_model",
            "validation_strategy",
            "risks",
            "financials",
            "full_plan",
        ]
        missing = [name for name in required_sections if not plan.get(name)]
        if missing:
            raise AssertionError(f"Missing generated sections: {missing}")
        if not plan.get("assumptions") or not plan.get("experiments"):
            raise AssertionError("Structured validation workspace was not generated.")
        linked_evidence = [
            item for item in plan.get("evidence_claims", []) if item.get("source_url")
        ]
        if len(linked_evidence) < 3:
            raise AssertionError("Grounded research did not persist enough linked sources.")
        if "http" not in plan["market_analysis"]:
            raise AssertionError("Market analysis does not contain inline source links.")
        financial_metrics = (plan.get("intelligence") or {}).get("financial_metrics") or {}
        required_financial_metrics = ["year_1_revenue", "arpu", "ltv", "blended_cac"]
        missing_metrics = [
            name for name in required_financial_metrics if not financial_metrics.get(name)
        ]
        if missing_metrics:
            raise AssertionError(
                f"Structured financial output is missing metrics: {missing_metrics}"
            )
        if financial_metrics["arpu"]["value"] == financial_metrics["ltv"]["value"]:
            raise AssertionError("ARPU and LTV were incorrectly stored as the same metric.")
        intelligence = plan.get("intelligence") or {}
        identity = intelligence.get("identity") or {}
        if not identity.get("name") or not identity.get("subtitle"):
            raise AssertionError("Concise venture identity was not generated.")
        if len(intelligence.get("capability_claims") or []) < 5:
            raise AssertionError("Capability maturity claims were not generated.")
        adjusted = intelligence.get("adjusted_score") or {}
        if adjusted.get("adjusted_score") is None:
            raise AssertionError("Evidence-adjusted viability score was not generated.")
        if any(
            not item.get("budget")
            or not item.get("success_metric")
            or "define" in item.get("success_metric", "").lower()
            for item in plan["experiments"]
        ):
            raise AssertionError("Validation experiments are not decision-ready.")
        print(
            json.dumps(
                {
                    "status": "passed",
                    "plan_status": plan["status"],
                    "viability_score": plan["viability_score"],
                    "sections": len(required_sections),
                    "assumptions": len(plan["assumptions"]),
                    "evidence_claims": len(plan["evidence_claims"]),
                    "linked_sources": len(linked_evidence),
                    "inline_citations": True,
                    "experiments": len(plan["experiments"]),
                    "structured_financial_metrics": len(
                        [value for value in financial_metrics.values() if value]
                    ),
                    "arpu": financial_metrics["arpu"]["display"],
                    "ltv": financial_metrics["ltv"]["display"],
                    "identity": identity["name"],
                    "adjusted_score": adjusted["adjusted_score"],
                    "evidence_confidence": adjusted["evidence_confidence"],
                    "capability_claims": len(intelligence["capability_claims"]),
                    "contradictions": len(intelligence.get("contradiction_issues") or []),
                    "financial_issues": len(intelligence.get("consistency_issues") or []),
                    "background_job": True,
                    "observed_stages": observed_stages,
                }
            )
        )
    finally:
        await cleanup(user_id)


if __name__ == "__main__":
    asyncio.run(main())
