# src/state.py
from typing import Optional

class AppState:
    """Tracks the workflow state for a startup idea."""
    def __init__(self, session_id: str, user_name: Optional[str] = None, consent: bool = False):
        self.session_id = session_id
        self.user_name = user_name
        self.consent = consent

        # Core workflow attributes
        self.idea: Optional[str] = None
        self.extra_info: Optional[str] = None
        self.market_analysis: Optional[str] = None
        self.business_model: Optional[str] = None
        self.validation_strategy: Optional[str] = None
        self.risks: Optional[str] = None
        self.financials: Optional[str] = None
        self.full_plan: Optional[str] = None

        # Branching decisions
        self.branch_to_market: bool = True
        self.go_to_risk: bool = True
