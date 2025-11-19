from typing import Tuple
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def validation_node(state: EntrepreneurState) -> Tuple[EntrepreneurState, str, callable]:
    idea = state.current_idea
    prompt = f"Provide validation strategies for this startup idea: {idea}"
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["validation"] = resp
    state.messages.append(resp)

    from src.nodes.risk_node import risk_node
    return state, resp, risk_node
