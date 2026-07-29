# backend/app/models/plan.py
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=True)
    idea = Column(Text, nullable=False)
    extra_info = Column(Text, nullable=True)
    market_analysis = Column(Text, nullable=True)
    business_model = Column(Text, nullable=True)
    validation_strategy = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)
    financials = Column(Text, nullable=True)
    full_plan = Column(Text, nullable=True)
    viability_score = Column(Integer, nullable=True)
    status = Column(String(50), default="draft")  # draft, generating, complete
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")
    messages = relationship("ChatMessage", back_populates="plan", cascade="all, delete-orphan")
    assumptions = relationship(
        "PlanAssumption",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="PlanAssumption.created_at",
    )
    evidence_claims = relationship(
        "EvidenceClaim",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="EvidenceClaim.created_at",
    )
    experiments = relationship(
        "ValidationExperiment",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ValidationExperiment.created_at",
    )
    generation_job = relationship(
        "PlanGenerationJob",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )
    intelligence = relationship(
        "PlanIntelligence",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="messages")


class PlanAssumption(Base):
    __tablename__ = "plan_assumptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(250), nullable=False)
    value = Column(String(250), nullable=False)
    category = Column(String(50), nullable=False, default="business")
    source_type = Column(String(30), nullable=False, default="ai_estimate")
    confidence = Column(Integer, nullable=False, default=25)
    impact = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="untested")
    validation_method = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="assumptions")


class EvidenceClaim(Base):
    __tablename__ = "evidence_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    claim = Column(Text, nullable=False)
    source_title = Column(String(500), nullable=True)
    source_url = Column(Text, nullable=True)
    source_date = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="unverified")
    confidence = Column(Integer, nullable=False, default=20)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="evidence_claims")


class ValidationExperiment(Base):
    __tablename__ = "validation_experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    hypothesis = Column(Text, nullable=True)
    method = Column(Text, nullable=True)
    success_metric = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="planned")
    priority = Column(String(20), nullable=False, default="high")
    budget = Column(String(100), nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="experiments")


class PlanGenerationJob(Base):
    __tablename__ = "plan_generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status = Column(String(30), nullable=False, default="queued")
    current_stage = Column(String(50), nullable=False, default="queued")
    progress = Column(Integer, nullable=False, default=0)
    message = Column(String(500), nullable=True)
    state_json = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)
    cancel_requested = Column(Boolean, nullable=False, default=False)
    attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="generation_job")


class PlanIntelligence(Base):
    __tablename__ = "plan_intelligence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    financial_metrics = Column(JSON, nullable=False, default=dict)
    market_metrics = Column(JSON, nullable=False, default=dict)
    contradiction_issues = Column(JSON, nullable=False, default=list)
    consistency_issues = Column(JSON, nullable=False, default=list)
    adjusted_score = Column(JSON, nullable=False, default=dict)
    identity = Column(JSON, nullable=False, default=dict)
    capability_claims = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("Plan", back_populates="intelligence")
