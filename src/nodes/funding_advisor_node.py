from typing import Tuple
from src.llm.groq_llm import ask_groq


def funding_advisor_node(state) -> Tuple:
    idea = state.current_idea
    prompt = (
    f"Act as a funding advisor for this startup idea: {idea}. "
    "Suggest 4 early-stage funding options (local-friendly), and give a 3-step plan to get started with each."
    )
    resp = ask_groq(prompt)
    state.ideas_data[idea]["funding_advice"] = resp
    return state, resp