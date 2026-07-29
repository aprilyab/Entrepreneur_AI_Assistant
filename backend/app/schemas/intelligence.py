"""Structured AI outputs used by deterministic product features."""

from typing import Literal

from pydantic import BaseModel, Field


class MetricValue(BaseModel):
    value: float
    display: str
    unit: str
    basis: str
    confidence: int = Field(ge=0, le=100)
    assumption: bool = True


class FundingAllocation(BaseModel):
    category: str
    percentage: float = Field(ge=0, le=100)
    amount: float = Field(ge=0)


class FinancialAssumption(BaseModel):
    name: str
    value: str
    rationale: str
    confidence: int = Field(ge=0, le=100)
    impact: Literal["high", "medium", "low"]
    validation_method: str


class FinancialMetrics(BaseModel):
    currency: str = "USD"
    year_1_revenue: MetricValue | None = None
    year_2_revenue: MetricValue | None = None
    year_3_revenue: MetricValue | None = None
    fixed_monthly_costs: MetricValue | None = None
    total_startup_costs: MetricValue | None = None
    cogs_per_unit: MetricValue | None = None
    inference_cost_per_render: MetricValue | None = None
    paid_cac: MetricValue | None = None
    blended_cac: MetricValue | None = None
    arpu: MetricValue | None = None
    gross_margin_rate: MetricValue | None = None
    ltv: MetricValue | None = None
    ltv_cac_ratio: MetricValue | None = None
    ltv_cac_denominator: Literal["paid_cac", "blended_cac"] | None = None
    monthly_churn_rate: MetricValue | None = None
    payback_months: MetricValue | None = None
    break_even_customers: MetricValue | None = None
    break_even_month: MetricValue | None = None
    minimum_funding: MetricValue | None = None
    recommended_funding: MetricValue | None = None
    use_of_funds: list[FundingAllocation] = Field(default_factory=list)
    assumptions: list[FinancialAssumption] = Field(default_factory=list)


class FinancialAgentOutput(BaseModel):
    report_markdown: str
    metrics: FinancialMetrics


class ContradictionIssue(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal[
        "market", "financial", "strategy", "timeline", "customer", "product", "risk", "other"
    ]
    claim_a: str
    claim_a_section: str
    claim_b: str
    claim_b_section: str
    explanation: str
    recommended_resolution: str


class ContradictionAuditOutput(BaseModel):
    issues: list[ContradictionIssue] = Field(default_factory=list)


class VentureIdentity(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    subtitle: str = Field(min_length=4, max_length=80)
    one_liner: str = Field(min_length=10, max_length=180)
    alternatives: list[str] = Field(default_factory=list, max_length=4)


class CapabilityClaim(BaseModel):
    capability: str
    status: Literal["existing", "proposed", "assumption"]
    evidence: str


class CapabilityAuditOutput(BaseModel):
    claims: list[CapabilityClaim] = Field(default_factory=list)


class ValidationExperimentDraft(BaseModel):
    title: str
    hypothesis: str
    method: str
    success_metric: str
    budget: str
    priority: Literal["high", "medium", "low"]


class ValidationAgentOutput(BaseModel):
    report_markdown: str
    viability_score: int = Field(ge=0, le=100)
    verdict: Literal["STRONG GO", "PROMISING", "NEEDS WORK", "RETHINK"]
    experiments: list[ValidationExperimentDraft] = Field(min_length=3, max_length=5)
