# backend/app/api/plans.py
import uuid
import asyncio
import logging
import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.plan import (
    Plan,
    ChatMessage,
    PlanAssumption,
    EvidenceClaim,
    ValidationExperiment,
    PlanGenerationJob,
    PlanIntelligence,
)
from app.schemas.plan import (
    PlanCreate, PlanResponse, PlanListResponse,
    ChatMessageCreate, ChatMessageResponse,
    AssumptionCreate, AssumptionUpdate, AssumptionResponse,
    EvidenceCreate, EvidenceUpdate, EvidenceResponse,
    ExperimentCreate, ExperimentUpdate, ExperimentResponse,
    GenerationJobResponse, PlanGenerationStarted,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/plans", tags=["plans"])
logger = logging.getLogger(__name__)


def _safe_export_filename(value: str | None, fallback: str) -> str:
    """Keep response headers portable and free from user-controlled delimiters."""
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", value or "").strip("-._")
    return (normalized[:80] or fallback).lower()


async def _refresh_adjusted_score(plan: Plan, db: AsyncSession):
    from app.services.evidence_scoring import evidence_adjusted_score

    assumptions = (
        await db.execute(select(PlanAssumption).where(PlanAssumption.plan_id == plan.id))
    ).scalars().all()
    evidence = (
        await db.execute(select(EvidenceClaim).where(EvidenceClaim.plan_id == plan.id))
    ).scalars().all()
    intelligence = (
        await db.execute(
            select(PlanIntelligence).where(PlanIntelligence.plan_id == plan.id)
        )
    ).scalar_one_or_none()
    if not intelligence:
        intelligence = PlanIntelligence(plan_id=plan.id)
        db.add(intelligence)
    intelligence.adjusted_score = evidence_adjusted_score(
        plan.viability_score or 0,
        list(assumptions),
        list(evidence),
    )


@router.post("", response_model=PlanGenerationStarted, status_code=status.HTTP_202_ACCEPTED)
async def create_plan(
    plan_data: PlanCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new business plan using the multi-agent workflow."""
    plan = Plan(
        user_id=user.id,
        idea=plan_data.idea,
        title=plan_data.title,
        extra_info=plan_data.extra_info,
        status="generating",
    )
    if not plan.title:
        plan.title = plan_data.idea[:100]
    db.add(plan)
    await db.flush()
    job = PlanGenerationJob(
        plan_id=plan.id,
        status="queued",
        current_stage="queued",
        progress=0,
        message="Your plan is queued for evidence-backed analysis.",
    )
    db.add(job)
    await db.commit()

    from app.services.generation_jobs import schedule_generation_job
    schedule_generation_job(job.id)
    return PlanGenerationStarted(id=plan.id, job_id=job.id, status=job.status)


async def _owned_plan(plan_id: uuid.UUID, user: User, db: AsyncSession) -> Plan:
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


async def _owned_job(
    plan_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> PlanGenerationJob:
    result = await db.execute(
        select(PlanGenerationJob)
        .join(Plan, Plan.id == PlanGenerationJob.plan_id)
        .where(PlanGenerationJob.plan_id == plan_id, Plan.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job


@router.get("/{plan_id}/generation", response_model=GenerationJobResponse)
async def get_generation_status(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return GenerationJobResponse.model_validate(await _owned_job(plan_id, user, db))


@router.post("/{plan_id}/generation/cancel", response_model=GenerationJobResponse)
async def cancel_generation(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await _owned_job(plan_id, user, db)
    if job.status in ("completed", "failed", "cancelled"):
        return GenerationJobResponse.model_validate(job)
    job.cancel_requested = True
    job.status = "cancelling"
    job.message = "Cancellation requested. The current agent will finish safely."
    await db.commit()
    await db.refresh(job)
    return GenerationJobResponse.model_validate(job)


@router.post("/{plan_id}/generation/resume", response_model=GenerationJobResponse)
async def resume_generation(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await _owned_job(plan_id, user, db)
    if job.status not in ("failed", "cancelled"):
        raise HTTPException(
            status_code=409,
            detail="Only failed or cancelled generation jobs can be resumed.",
        )
    plan = await _owned_plan(plan_id, user, db)
    job.status = "queued"
    job.current_stage = "queued"
    job.cancel_requested = False
    job.error_type = None
    job.completed_at = None
    job.message = "Queued to resume from the last saved agent state…"
    plan.status = "generating"
    await db.commit()
    await db.refresh(job)

    from app.services.generation_jobs import schedule_generation_job
    schedule_generation_job(job.id)
    return GenerationJobResponse.model_validate(job)


@router.post("/{plan_id}/validation-workspace/bootstrap", response_model=PlanResponse)
async def bootstrap_workspace(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create structured validation records for an existing generated plan."""
    plan = await _owned_plan(plan_id, user, db)
    from app.services.validation_workspace import bootstrap_validation_workspace

    assumptions, evidence_claims, experiments = bootstrap_validation_workspace(plan)
    if not plan.assumptions:
        plan.assumptions.extend(assumptions)
    if not plan.evidence_claims:
        plan.evidence_claims.extend(evidence_claims)
    if not plan.experiments:
        plan.experiments.extend(experiments)
    await db.commit()
    await db.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.post("/{plan_id}/research/refresh", response_model=PlanResponse)
async def refresh_grounded_research(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refresh market analysis and sourced evidence with live web research."""
    plan = await _owned_plan(plan_id, user, db)
    from app.services.grounded_research import grounded_market_analysis
    from app.services.validation_workspace import build_evidence_claims

    analysis, sources = await asyncio.to_thread(
        grounded_market_analysis,
        plan.idea,
        plan.extra_info or "",
    )
    if not analysis or not sources:
        raise HTTPException(
            status_code=503,
            detail="Live research is temporarily unavailable. The existing analysis was preserved.",
        )

    result = await db.execute(
        select(EvidenceClaim).where(EvidenceClaim.plan_id == plan.id)
    )
    preserved_keys: set[str] = set()
    for item in result.scalars().all():
        notes = item.notes or ""
        generated = (
            item.status == "sourced"
            or notes.startswith("[auto:")
            or notes.startswith("AI-generated claim.")
            or notes.startswith("Retrieved during live research")
        )
        if item.status not in ("verified", "disputed") and generated:
            await db.delete(item)
        else:
            preserved_keys.add(" ".join(re.findall(r"[a-z0-9]+", item.claim.lower())))

    plan.market_analysis = analysis
    refreshed_evidence = [
        item
        for item in build_evidence_claims(plan, sources)
        if " ".join(re.findall(r"[a-z0-9]+", item.claim.lower())) not in preserved_keys
    ]
    db.add_all(refreshed_evidence)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()
    await db.refresh(
        plan,
        attribute_names=["assumptions", "evidence_claims", "experiments"],
    )
    return PlanResponse.model_validate(plan)


@router.post("/{plan_id}/assumptions", response_model=AssumptionResponse, status_code=201)
async def create_assumption(
    plan_id: uuid.UUID,
    data: AssumptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await _owned_plan(plan_id, user, db)
    assumption = PlanAssumption(plan_id=plan.id, **data.model_dump())
    db.add(assumption)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()
    await db.refresh(assumption)
    return AssumptionResponse.model_validate(assumption)


@router.patch("/{plan_id}/assumptions/{item_id}", response_model=AssumptionResponse)
async def update_assumption(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    data: AssumptionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(PlanAssumption).where(
            PlanAssumption.id == item_id, PlanAssumption.plan_id == plan_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Assumption not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()
    await db.refresh(item)
    return AssumptionResponse.model_validate(item)


@router.delete("/{plan_id}/assumptions/{item_id}", status_code=204)
async def delete_assumption(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(PlanAssumption).where(
            PlanAssumption.id == item_id, PlanAssumption.plan_id == plan_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Assumption not found")
    await db.delete(item)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()


@router.post("/{plan_id}/evidence", response_model=EvidenceResponse, status_code=201)
async def create_evidence(
    plan_id: uuid.UUID,
    data: EvidenceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await _owned_plan(plan_id, user, db)
    item = EvidenceClaim(plan_id=plan.id, **data.model_dump())
    db.add(item)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()
    await db.refresh(item)
    return EvidenceResponse.model_validate(item)


@router.patch("/{plan_id}/evidence/{item_id}", response_model=EvidenceResponse)
async def update_evidence(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    data: EvidenceUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(EvidenceClaim).where(
            EvidenceClaim.id == item_id, EvidenceClaim.plan_id == plan_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Evidence claim not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()
    await db.refresh(item)
    return EvidenceResponse.model_validate(item)


@router.delete("/{plan_id}/evidence/{item_id}", status_code=204)
async def delete_evidence(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(EvidenceClaim).where(
            EvidenceClaim.id == item_id, EvidenceClaim.plan_id == plan_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Evidence claim not found")
    await db.delete(item)
    await db.flush()
    await _refresh_adjusted_score(plan, db)
    await db.commit()


@router.post("/{plan_id}/experiments", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    plan_id: uuid.UUID,
    data: ExperimentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan = await _owned_plan(plan_id, user, db)
    item = ValidationExperiment(plan_id=plan.id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ExperimentResponse.model_validate(item)


@router.patch("/{plan_id}/experiments/{item_id}", response_model=ExperimentResponse)
async def update_experiment(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    data: ExperimentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(ValidationExperiment).where(
            ValidationExperiment.id == item_id,
            ValidationExperiment.plan_id == plan_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return ExperimentResponse.model_validate(item)


@router.delete("/{plan_id}/experiments/{item_id}", status_code=204)
async def delete_experiment(
    plan_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _owned_plan(plan_id, user, db)
    result = await db.execute(
        select(ValidationExperiment).where(
            ValidationExperiment.id == item_id,
            ValidationExperiment.plan_id == plan_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Experiment not found")
    await db.delete(item)
    await db.commit()


@router.get("", response_model=list[PlanListResponse])
async def list_plans(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all plans for the current user."""
    result = await db.execute(
        select(Plan)
        .where(Plan.user_id == user.id)
        .order_by(Plan.created_at.desc())
    )
    plans = result.scalars().all()
    return [PlanListResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific plan with full details."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a plan."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    await db.delete(plan)
    await db.commit()


@router.post("/{plan_id}/chat", response_model=ChatMessageResponse)
async def chat_about_plan(
    plan_id: uuid.UUID,
    message_data: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ask a follow-up question about a plan."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Save user message
    user_msg = ChatMessage(plan_id=plan.id, role="user", content=message_data.message)
    db.add(user_msg)

    # Generate AI response with context
    from app.services.llm import ask_llm
    context = f"""
    You are an AI business mentor helping an entrepreneur.

    Their startup idea: {plan.idea}
    Their full business plan: {plan.full_plan or 'Not yet generated'}

    The entrepreneur asks: {message_data.message}

    Provide a helpful, actionable, and specific answer. Reference their business plan when relevant.
    Be conversational but professional.
    """
    answer = await asyncio.to_thread(ask_llm, context)

    # Save assistant message
    assistant_msg = ChatMessage(plan_id=plan.id, role="assistant", content=answer)
    db.add(assistant_msg)
    await db.flush()
    await db.commit()
    await db.refresh(assistant_msg)

    return ChatMessageResponse.model_validate(assistant_msg)


@router.get("/{plan_id}/export/pdf")
async def export_plan_pdf(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export plan as a formatted PDF."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    from app.utils.exports import export_plan_as_pdf
    pdf_bytes = export_plan_as_pdf({
        "title": plan.title,
        "idea": plan.idea,
        "market_analysis": plan.market_analysis,
        "business_model": plan.business_model,
        "validation_strategy": plan.validation_strategy,
        "risks": plan.risks,
        "financials": plan.financials,
        "full_plan": plan.full_plan,
        "intelligence": {
            "identity": plan.intelligence.identity if plan.intelligence else {},
            "adjusted_score": plan.intelligence.adjusted_score if plan.intelligence else {},
            "financial_metrics": plan.intelligence.financial_metrics if plan.intelligence else {},
            "contradiction_issues": plan.intelligence.contradiction_issues if plan.intelligence else [],
            "consistency_issues": plan.intelligence.consistency_issues if plan.intelligence else [],
        },
    })

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_safe_export_filename(plan.title, "business-plan")}.pdf"'
            )
        },
    )


@router.get("/{plan_id}/export/pptx")
async def export_plan_pptx(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export plan as a PowerPoint pitch deck."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if not plan.full_plan:
        raise HTTPException(status_code=400, detail="Plan must be complete before export")

    from app.services.pitch_deck import get_pitch_generator
    generator = get_pitch_generator()
    pptx_bytes = generator.generate({
        "title": plan.title,
        "idea": plan.idea,
        "market_analysis": plan.market_analysis,
        "business_model": plan.business_model,
        "validation_strategy": plan.validation_strategy,
        "risks": plan.risks,
        "financials": plan.financials,
        "full_plan": plan.full_plan,
        "viability_score": plan.viability_score,
        "intelligence": {
            "identity": plan.intelligence.identity if plan.intelligence else {},
            "adjusted_score": plan.intelligence.adjusted_score if plan.intelligence else {},
            "financial_metrics": plan.intelligence.financial_metrics if plan.intelligence else {},
            "contradiction_issues": plan.intelligence.contradiction_issues if plan.intelligence else [],
            "consistency_issues": plan.intelligence.consistency_issues if plan.intelligence else [],
        },
    })

    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_safe_export_filename(plan.title, "pitch-deck")}.pptx"'
            )
        },
    )


@router.get("/{plan_id}/export/excel")
async def export_plan_excel(
    plan_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export financial projections as Excel."""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    from app.utils.exports import export_financials_as_excel
    excel_bytes = export_financials_as_excel(
        plan.financials or "",
        plan.intelligence.financial_metrics if plan.intelligence else {},
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{_safe_export_filename(plan.title, "financials")}.xlsx"'
            )
        },
    )
