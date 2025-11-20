from src.state import AppState
from src.llm.gemini_llm import ask_gemini

def business_plan_node(state: AppState) -> AppState:
    prompt = (
        f"Compile a full business plan with sections:\n"
        f"Idea: {state.idea}\nExtra Info: {state.extra_info}\nMarket Analysis: {state.market_analysis}\n"
        f"Business Model: {state.business_model}\nValidation: {state.validation_strategy}\n"
        f"Risks: {state.risks}\nFinancials: {state.financials}\n"
    )
    state.full_plan = ask_gemini(prompt)
    return state
