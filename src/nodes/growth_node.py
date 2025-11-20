from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def growth_node(state: AppState) -> AppState:
    if not state.financials:
        prompt = f"Propose a growth plan and financial strategy for the startup:\nIdea: {state.idea}"
        state.financials = ask_gemini(prompt)
    return state
