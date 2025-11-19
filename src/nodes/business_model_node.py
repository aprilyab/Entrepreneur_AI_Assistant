from typing import Tuple
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def business_model_node(state: EntrepreneurState) -> Tuple[EntrepreneurState, str, callable]:
    idea = state.current_idea
    prompt = f"Suggest a business model for this startup idea: {idea}"
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["business_model"] = resp
    state.messages.append(resp)

    from src.nodes.validation_node import validation_node
    return state, resp, validation_node
