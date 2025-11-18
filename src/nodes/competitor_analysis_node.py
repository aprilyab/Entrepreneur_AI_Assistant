from typing import Tuple
from src.llm.groq_llm import ask_groq


def competitor_analysis_node(state) -> Tuple:
    idea = state.current_idea
    prompt = f"For the idea {idea}, list 5 potential competitors or alternative solutions and one-sentence comparison for each."
    resp = ask_groq(prompt)
    state.ideas_data[idea]["competitors"] = resp
    return state, resp