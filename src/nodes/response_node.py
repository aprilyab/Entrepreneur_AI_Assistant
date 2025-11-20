from typing import Tuple, Optional
from src.state import AppState

def response_node(state: AppState) -> Tuple[AppState, str, Optional[callable]]:
    idea = state.current_idea
    idea_data = state.ideas_data.get(idea, {})

    final_output = f"### Final Startup Plan: {idea}\n"
    for k, v in idea_data.items():
        final_output += f"\n**{k.capitalize()}**:\n{v}\n"

    return state, final_output, None  # Workflow ends
