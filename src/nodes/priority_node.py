from typing import Tuple
from src.llm.groq_llm import ask_groq


def priority_node(state) -> Tuple:
    idea = state.current_idea
    steps = [s.description for s in state.steps]
    prompt = f"Assign priority High/Medium/Low to each of these tasks (one per line as `task | prior