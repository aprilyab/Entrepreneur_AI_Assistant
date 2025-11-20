# src/nodes/decision_node.py
from src.state import AppState

def decision_node(state: AppState) -> AppState:
    """
    Decide the next branch based on existing data.
    - If market_analysis exists and mentions risk, go to risk_node.
    - Otherwise, go to growth_node.
    """
    # Safe access: use empty string if attribute is None
    market_info = getattr(state, "market_analysis", "")
    if market_info is None:
        market_info = ""

    # Example decision logic
    if "risk" in market_info.lower() or "uncertain" in market_info.lower():
        state.go_to_risk = True
    else:
        state.go_to_risk = False

    # You can also set branch_to_market for initial branching
    if not hasattr(state, "branch_to_market"):
        state.branch_to_market = True  # default branch

    return state
