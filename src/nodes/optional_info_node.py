from src.state import AppState

def optional_info_node(state: AppState) -> AppState:
    # For simplicity, we add default extra info
    if not state.extra_info:
        state.extra_info = "Some extra optional information"
    return state
