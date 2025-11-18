from typing import Tuple
from src.llm.groq_llm import ask_groq


def market_research_node(state) -> Tuple:
    idea = state.current_idea
    prompt = f"Provide a short market research summary for this idea: {idea}. Include customer segments and top 3 competitor types."
    resp = ask_groq(prompt)
    state.ideas_data[idea]["market_research"] = resp
    return state, resp