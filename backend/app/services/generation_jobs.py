"""Persistent background execution for resumable business-plan generation."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.database import async_session
from app.models.plan import Plan, PlanGenerationJob, PlanIntelligence
from app.services.workflow import WorkflowCancelled, run_business_plan_workflow
from app.services.validation_workspace import bootstrap_validation_workspace
from app.services.evidence_scoring import evidence_adjusted_score

logger = logging.getLogger(__name__)
_active_tasks: dict[UUID, asyncio.Task] = {}


STAGE_START = {
    "market": (5, "Searching the market and collecting sources…"),
    "identity": (20, "Creating a concise venture identity…"),
    "strategy": (22, "Designing the business model and strategy…"),
    "capabilities": (35, "Separating current capabilities from proposals…"),
    "finance": (38, "Building financial assumptions and scenarios…"),
    "check_finance": (51, "Checking financial arithmetic and allocations…"),
    "risk": (54, "Stress-testing risks and mitigations…"),
    "growth": (68, "Designing the growth strategy…"),
    "validate": (81, "Scoring viability and validation priorities…"),
    "audit": (91, "Checking the reports for contradictions…"),
    "compile": (96, "Compiling the final venture plan…"),
}

STAGE_COMPLETE = {
    "market": (18, "Market research and source collection complete."),
    "identity": (21, "Venture identity complete."),
    "strategy": (34, "Business model and strategy complete."),
    "capabilities": (36, "Capability maturity labels complete."),
    "finance": (50, "Financial analysis complete."),
    "check_finance": (53, "Deterministic financial checks complete."),
    "risk": (64, "Risk assessment complete."),
    "growth": (77, "Growth strategy complete."),
    "validate": (90, "Viability decision complete."),
    "audit": (95, "Cross-section consistency audit complete."),
    "compile": (98, "Final plan compiled. Saving validation workspace…"),
}


def _stage_update(node_name: str, state: dict, current_progress: int) -> tuple[str, int, str]:
    if node_name == "supervisor":
        stage = state.get("current_agent", "queued")
        progress, message = STAGE_START.get(stage, (current_progress, "Coordinating specialist agents…"))
        return stage, max(current_progress, progress), message
    if node_name in STAGE_COMPLETE:
        progress, message = STAGE_COMPLETE[node_name]
        return node_name, max(current_progress, progress), message
    return state.get("current_agent", "running"), current_progress, "Saving agent progress…"


async def _cancel_requested(job_id: UUID) -> bool:
    async with async_session() as session:
        value = await session.scalar(
            select(PlanGenerationJob.cancel_requested).where(PlanGenerationJob.id == job_id)
        )
        return True if value is None else bool(value)


async def _persist_progress(job_id: UUID, node_name: str, state: dict):
    async with async_session() as session:
        job = await session.get(PlanGenerationJob, job_id)
        if not job:
            return
        plan = await session.get(Plan, job.plan_id)
        if not plan:
            return

        stage, progress, message = _stage_update(node_name, state, job.progress)
        job.status = "running"
        job.current_stage = stage
        job.progress = progress
        job.message = message
        job.state_json = json.dumps(state)

        plan.market_analysis = state.get("market_analysis") or plan.market_analysis
        plan.business_model = state.get("business_model") or plan.business_model
        plan.financials = state.get("financials") or plan.financials
        plan.risks = state.get("risks") or plan.risks
        plan.validation_strategy = state.get("validation_strategy") or plan.validation_strategy
        plan.viability_score = state.get("viability_score") or plan.viability_score
        plan.full_plan = state.get("full_plan") or plan.full_plan
        if state.get("financial_metrics"):
            intelligence = await session.scalar(
                select(PlanIntelligence).where(PlanIntelligence.plan_id == plan.id)
            )
            if not intelligence:
                intelligence = PlanIntelligence(plan_id=plan.id)
                session.add(intelligence)
            intelligence.financial_metrics = state["financial_metrics"]
            if "contradiction_issues" in state:
                intelligence.contradiction_issues = state["contradiction_issues"]
            if "consistency_issues" in state:
                intelligence.consistency_issues = state["consistency_issues"]
            if state.get("identity"):
                intelligence.identity = state["identity"]
            if state.get("capability_claims"):
                intelligence.capability_claims = state["capability_claims"]
        await session.commit()


async def _mark_terminal(
    job_id: UUID,
    *,
    status: str,
    message: str,
    error_type: str | None = None,
):
    async with async_session() as session:
        job = await session.get(PlanGenerationJob, job_id)
        if not job:
            return
        plan = await session.get(Plan, job.plan_id)
        job.status = status
        job.current_stage = status
        job.message = message
        job.error_type = error_type
        job.completed_at = datetime.utcnow()
        if plan:
            plan.status = "error" if status == "failed" else status
        await session.commit()


async def _finalize(job_id: UUID, result: dict):
    async with async_session() as session:
        job = await session.get(PlanGenerationJob, job_id)
        if not job:
            return
        plan = await session.get(Plan, job.plan_id)
        if not plan:
            return

        plan.market_analysis = result.get("market_analysis", "")
        plan.business_model = result.get("business_model", "")
        plan.validation_strategy = result.get("validation_strategy", "")
        plan.risks = result.get("risks", "")
        plan.financials = result.get("financials", "")
        plan.full_plan = result.get("full_plan", "")
        plan.viability_score = result.get("viability_score", 0)
        plan.status = "complete"

        intelligence = await session.scalar(
            select(PlanIntelligence).where(PlanIntelligence.plan_id == plan.id)
        )
        if not intelligence:
            intelligence = PlanIntelligence(plan_id=plan.id)
            session.add(intelligence)
        intelligence.financial_metrics = result.get("financial_metrics", {})
        intelligence.contradiction_issues = result.get("contradiction_issues", [])
        intelligence.consistency_issues = result.get("consistency_issues", [])
        intelligence.identity = result.get("identity", {})
        intelligence.capability_claims = result.get("capability_claims", [])
        generated_name = intelligence.identity.get("name")
        if generated_name and (not plan.title or plan.title == plan.idea[:100]):
            plan.title = generated_name

        assumptions, evidence_claims, experiments = bootstrap_validation_workspace(
            plan,
            result.get("research_sources", []),
            result.get("financial_metrics", {}),
            result.get("validation_experiments", []),
        )
        session.add_all([*assumptions, *evidence_claims, *experiments])
        intelligence.adjusted_score = evidence_adjusted_score(
            plan.viability_score or 0,
            assumptions,
            evidence_claims,
        )

        job.status = "completed"
        job.current_stage = "complete"
        job.progress = 100
        job.message = "Your evidence-backed venture plan is ready."
        job.state_json = json.dumps(result)
        job.error_type = None
        job.cancel_requested = False
        job.completed_at = datetime.utcnow()
        await session.commit()


async def run_generation_job(job_id: UUID):
    """Run or resume one generation job without blocking the API event loop."""
    async with async_session() as session:
        job = await session.get(PlanGenerationJob, job_id)
        if not job:
            return
        plan = await session.get(Plan, job.plan_id)
        if not plan:
            return
        if job.cancel_requested:
            await _mark_terminal(
                job_id,
                status="cancelled",
                message="Generation was cancelled before it started.",
            )
            return

        idea = plan.idea
        extra_info = plan.extra_info or ""
        saved_state = json.loads(job.state_json) if job.state_json else None
        job.status = "running"
        job.current_stage = "starting"
        job.progress = max(1, job.progress)
        job.message = "Starting the specialist-agent workflow…"
        job.error_type = None
        job.started_at = job.started_at or datetime.utcnow()
        job.completed_at = None
        job.attempts += 1
        plan.status = "generating"
        await session.commit()

    loop = asyncio.get_running_loop()

    def progress_callback(node_name: str, state: dict):
        future = asyncio.run_coroutine_threadsafe(
            _persist_progress(job_id, node_name, state),
            loop,
        )
        future.result(timeout=30)

    def cancel_check() -> bool:
        future = asyncio.run_coroutine_threadsafe(_cancel_requested(job_id), loop)
        return bool(future.result(timeout=15))

    try:
        result = await asyncio.to_thread(
            run_business_plan_workflow,
            idea,
            extra_info,
            saved_state=saved_state,
            progress_callback=progress_callback,
            cancel_check=cancel_check,
        )
        await _finalize(job_id, result)
    except WorkflowCancelled:
        await _mark_terminal(
            job_id,
            status="cancelled",
            message="Generation stopped safely. Resume whenever you are ready.",
        )
    except Exception as exc:
        logger.error(
            "Background generation failed job_id=%s error_type=%s",
            job_id,
            type(exc).__name__,
        )
        await _mark_terminal(
            job_id,
            status="failed",
            message="An agent failed. Your completed stages were saved and can be resumed.",
            error_type=type(exc).__name__,
        )


def schedule_generation_job(job_id: UUID):
    existing = _active_tasks.get(job_id)
    if existing and not existing.done():
        return
    task = asyncio.create_task(run_generation_job(job_id))
    _active_tasks[job_id] = task
    task.add_done_callback(lambda _: _active_tasks.pop(job_id, None))


async def recover_incomplete_generation_jobs():
    """Resume queued/running jobs after an application restart."""
    async with async_session() as session:
        result = await session.execute(
            select(PlanGenerationJob).where(
                PlanGenerationJob.status.in_(["queued", "running", "cancelling"])
            )
        )
        jobs = result.scalars().all()
        for job in jobs:
            if job.cancel_requested:
                job.status = "cancelled"
                job.current_stage = "cancelled"
                job.message = "Generation was cancelled during application restart."
                job.completed_at = datetime.utcnow()
            else:
                job.status = "queued"
                job.message = "Recovered after application restart; resuming saved progress…"
        await session.commit()

    for job in jobs:
        if not job.cancel_requested:
            schedule_generation_job(job.id)
