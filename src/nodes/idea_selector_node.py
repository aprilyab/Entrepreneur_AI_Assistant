from typing import Tuple
from src.llm.groq_llm import ask_groq


def idea_selector_node(state, selection_text: str) -> Tuple:
    """Handles user's selection (online/offline/hybrid or choose idea)."""
    state.messages.append(selection_text)
    # If user selects one of the keywords, store in ideas_data
    sel = selection_text.lower()
    if state.current_idea:
        state.ideas_data[state.current_idea]["delivery"] = sel
    # Ask for model preference next
    prompt = f"User selected: {sel}. Ask the user which business model they prefer (give 3 suggestions)."
    resp = ask_groq(prompt)
    return state, resp