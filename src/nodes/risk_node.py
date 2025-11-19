from typing import Tuple
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def risk_node(state: EntrepreneurState) -> Tuple[EntrepreneurState, str, callable]:
    idea = state.current_idea
    prompt = f"Identify risks and mitigation strategies for: {idea}"
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["risks"] = resp
    state.messages.append(resp)

    from src.nodes.growth_node import growth_node
    return state, resp, growth_node
