from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Task(BaseModel):
    id: str
    description: str
    due: Optional[str] = None
    priority: Optional[str] = None
    scheduled_at: Optional[str] = None
    status: str = "pending"


class EntrepreneurState(BaseModel):
    session_id: str
    user_name: Optional[str] = None
    consent: bool = False
    messages: List[str] = Field(default_factory=list)
    startup_idea: Optional[str] = None
    chosen_model: Optional[str] = None
    steps: List[Task] = Field(default_factory=list)
    pending_clarifications: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))