# src/nodes/followup_node.py
from src.llm.gemini_llm import ask_gemini
from src.state import AppState
from typing import Tuple

def followup_node(state: AppState, question: str) -> Tuple[AppState, str]:
    """
    Handles follow-up questions after the business plan has been generated.
    """
    prompt = (
        f"You are an AI assistant helping an entrepreneur.\n"
        f"Startup idea: {getattr(state, 'idea', '[No idea]')}\n"
        f"Business plan so far:\n{getattr(state, 'full_plan', '[No plan generated]')}\n\n"
        f"User question: {question}\n"
        f"Provide a helpful, concise answer."
    )

    answer = ask_gemini(prompt)
    return state, answer
