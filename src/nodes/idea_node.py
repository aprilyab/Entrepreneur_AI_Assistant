from typing import Optional
from src.state import AppState

def idea_node(state: AppState, user_input: Optional[str] = None) -> AppState:
    if user_input and user_input.strip():
        state.idea = user_input.strip()
    else:
        state.idea = "Default startup idea"
    return state
