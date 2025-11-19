from typing import Tuple
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def market_node(state: EntrepreneurState) -> Tuple[EntrepreneurState, str, callable]:
    idea = state.current_idea
    prompt = f"Analyze market opportunities, competition, and trends for this idea:\n{idea}\nSummarize in bullets."
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["market_analysis"] = resp
    state.messages.append(resp)

    from src.nodes.business_model_node import business_model_node
    return state, resp, business_model_node
