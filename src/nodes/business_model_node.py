from typing import Tuple
from src.llm.groq_llm import ask_groq


def business_model_node(state) -> Tuple:
    idea = state.current_idea
    prompt = f"Suggest 3 suitable business models for this idea: {idea}. Return short label and one-line justification."
    resp = ask_groq(prompt)
    state.ideas_data[idea]["business_models"] = resp
    return state, resp