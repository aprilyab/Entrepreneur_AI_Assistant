# backend/app/schemas/plan.py
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class AssumptionBase(BaseModel):
    name: str = Field(min_length=1, max_length=250)
    value: str = Field(min_length=1, max_length=250)
    category: str = Field(default="business", max_length=50)
    source_type: str = Field(default="ai_estimate", max_length=30)
    confidence: int = Field(default=25, ge=0, le=100)
    impact: str = Field(default="medium", max_length=20)
    status: str = Field(default="untested", max_length=20)
    validation_method: Optional[str] = None


class AssumptionCreate(AssumptionBase):
    pass


class AssumptionUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    category: Optional[str] = None
    source_type: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    impact: Optional[str] = None
    status: Optional[str] = None
    validation_method: Optional[str] = None


class AssumptionResponse(AssumptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class EvidenceBase(BaseModel):
    claim: str = Field(min_length=1, max_length=10_000)
    source_title: Optional[str] = Field(default=None, max_length=500)
    source_url: Optional[str] = None
    source_date: Optional[str] = None
    status: str = "unverified"
    confidence: int = Field(default=20, ge=0, le=100)
    notes: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    pass


class EvidenceUpdate(BaseModel):
    claim: Optional[str] = None
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    source_date: Optional[str] = None
    status: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None


class EvidenceResponse(EvidenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ExperimentBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    hypothesis: Optional[str] = None
    method: Optional[str] = None
    success_metric: Optional[str] = None
    status: str = "planned"
    priority: str = "high"
    budget: Optional[str] = None
    result: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    title: Optional[str] = None
    hypothesis: Optional[str] = None
    method: Optional[str] = None
    success_metric: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    budget: Optional[str] = None
    result: Optional[str] = None


class ExperimentResponse(ExperimentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class GenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plan_id: UUID
    status: str
    current_stage: str
    progress: int
    message: Optional[str]
    error_type: Optional[str]
    cancel_requested: bool
    attempts: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: datetime

class PlanGenerationStarted(BaseModel):
    id: UUID
    job_id: UUID
    status: str


class PlanIntelligenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    financial_metrics: dict = Field(default_factory=dict)
    market_metrics: dict = Field(default_factory=dict)
    contradiction_issues: list = Field(default_factory=list)
    consistency_issues: list = Field(default_factory=list)
    adjusted_score: dict = Field(default_factory=dict)
    identity: dict = Field(default_factory=dict)
    capability_claims: list = Field(default_factory=list)

class PlanCreate(BaseModel):
    idea: str = Field(min_length=10, max_length=10_000)
    title: Optional[str] = Field(default=None, max_length=500)
    extra_info: Optional[str] = Field(default=None, max_length=20_000)


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: Optional[str]
    idea: str
    extra_info: Optional[str]
    market_analysis: Optional[str]
    business_model: Optional[str]
    validation_strategy: Optional[str]
    risks: Optional[str]
    financials: Optional[str]
    full_plan: Optional[str]
    viability_score: Optional[int]
    status: str
    assumptions: list[AssumptionResponse] = Field(default_factory=list)
    evidence_claims: list[EvidenceResponse] = Field(default_factory=list)
    experiments: list[ExperimentResponse] = Field(default_factory=list)
    generation_job: Optional[GenerationJobResponse] = None
    intelligence: Optional[PlanIntelligenceResponse] = None
    created_at: datetime
    updated_at: datetime

class PlanListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: Optional[str]
    idea: str
    viability_score: Optional[int]
    status: str
    created_at: datetime

class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=10_000)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime



class ViabilityScoreResponse(BaseModel):
    score: int
    verdict: str
    breakdown: dict
    green_flags: list[str]
    red_flags: list[str]
    recommendation: str
    next_steps: list[str]
