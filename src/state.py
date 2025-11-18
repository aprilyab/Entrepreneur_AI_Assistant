from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Task(BaseModel):
    """
    Represents a single actionable step in a startup plan.
    """
    id: str  # Unique identifier for the task (e.g., UUID)
    description: str  # Short description of the task
    priority: Optional[str] = None  # Priority level (High/Medium/Low)
    scheduled_at: Optional[str] = None  # Scheduled time (ISO format or readable string)
    status: str = "pending"  # Task status (pending, in-progress, completed)


class EntrepreneurState(BaseModel):
    """
    Tracks the user's session state, including messages, startup ideas, and plan steps.
    """
    session_id: str  # Unique ID for this user session
    user_name: Optional[str] = None  # Name of the user
    consent: bool = False  # Whether the user has agreed to terms
    messages: List[str] = Field(default_factory=list)  # Conversation messages in this session

    # Multiple startup ideas support
    ideas: List[str] = Field(default_factory=list)  # List of all ideas provided by the user
    current_idea: Optional[str] = None  # The idea currently being worked on
    ideas_data: Dict[str, Dict] = Field(default_factory=dict)  
    # Structured data for each idea (plan, priorities, schedules, etc.)

    # Working plan for the current idea
    steps: List[Task] = Field(default_factory=list)  # Tasks/steps for the current idea
    pending_clarifications: List[str] = Field(default_factory=list)  
    # Questions awaiting user clarification

    created_at: datetime = Field(default_factory=datetime.utcnow)  
    # Timestamp when this session was created
