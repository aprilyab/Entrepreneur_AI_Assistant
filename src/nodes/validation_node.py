from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def validation_node(state: AppState) -> AppState:
    if not state.validation_strategy:
        prompt = f"Propose a validation strategy for the startup:\nIdea: {state.idea}"
        state.validation_strategy = ask_gemini(prompt)
    return state
