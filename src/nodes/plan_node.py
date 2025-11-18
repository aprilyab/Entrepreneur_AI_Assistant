from typing import Tuple
from uuid import uuid4
from src.state import Task
from src.llm.groq_llm import ask_groq


def plan_node(state) -> Tuple:
    idea = state.current_idea
    model = state.ideas_data[idea].get("chosen_model") or state.ideas_data[idea].get("business_models")
    prompt = f"Generate 5 actionable startup steps for idea: {idea} using model: {model}. Return as 1-per-line bullets."
    resp = ask_groq(prompt)
    steps = []
    for line in resp.split('\n'):
        clean = line.strip('-• \t')
        if clean:
            steps.append(Task(id=str(uuid4()), description=clean))
    state.steps = steps
    state.ideas_data[idea]["steps"] = [s.dict() for s in steps]
    return state, resp