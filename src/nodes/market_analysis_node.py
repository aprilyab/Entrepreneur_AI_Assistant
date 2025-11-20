from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def market_analysis_node(state: AppState) -> AppState:
    if not state.market_analysis:
        prompt = f"Analyze the market for this startup idea:\n{state.idea}"
        state.market_analysis = ask_gemini(prompt)
    return state
