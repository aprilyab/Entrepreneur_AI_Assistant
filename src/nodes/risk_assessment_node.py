from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def risk_node(state: AppState) -> AppState:
    if not state.risks:
        prompt = f"Identify key risks for the startup idea:\nIdea: {state.idea}"
        state.risks = ask_gemini(prompt)
    return state
