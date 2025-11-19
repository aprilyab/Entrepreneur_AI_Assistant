from typing import Tuple
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini
from src.nodes.response_node import response_node

def growth_node(state: EntrepreneurState) -> Tuple[EntrepreneurState, str, callable]:
    idea = state.current_idea
    prompt = f"List growth strategies and opportunities for: {idea}"
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["growth"] = resp
    state.messages.append(resp)

    return state, resp, response_node
