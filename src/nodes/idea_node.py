from typing import Tuple
from src import state
from src.llm.groq_llm import ask_groq


def idea_node(state, user_text: str) -> Tuple:
    """Accepts free-text idea, sets current idea and returns follow-up question."""
    state.messages.append(user_text)
    prompt = f"Summarize this startup idea concisely and ask whether the user prefers online, offline, or hybrid: {user_text}"
    resp = ask_groq(prompt)
    # Set current idea as raw for now
    state.current_idea = user_text
    if user_text not in state.ideas:
        state.ideas.append(user_text)
        state.ideas_data[user_text] = {}
    return state, resp