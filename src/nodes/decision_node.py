# src/nodes/decision_node.py
from typing import Tuple, Optional
from src.state import EntrepreneurState

def decision_node(state: EntrepreneurState, user_input: Optional[str] = None) -> Tuple[EntrepreneurState, str, Optional[callable]]:
    choice = user_input.lower() if user_input else None
    if not choice:
        return state, "Next step: risk or growth?", decision_node

    state.messages.append(f"User chose: {choice}")
    # Local import
    if choice == "risk":
        from src.nodes.risk_node import risk_node
        next_node = risk_node
    else:
        from src.nodes.growth_node import growth_node
        next_node = growth_node

    return state, f"Proceeding with {choice} strategy.", next_node
