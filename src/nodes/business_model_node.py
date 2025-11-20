from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def business_model_node(state: AppState) -> AppState:
    if not state.business_model:
        prompt = f"Create a business model for this startup idea and market analysis:\nIdea: {state.idea}\nMarket: {state.market_analysis}"
        state.business_model = ask_gemini(prompt)
    return state
