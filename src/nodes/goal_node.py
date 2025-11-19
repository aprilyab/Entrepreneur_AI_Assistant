from typing import Tuple, Optional, Callable
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def goal_node(
    state: EntrepreneurState, 
    user_input: Optional[str] = None
) -> Tuple[EntrepreneurState, str, Optional[Callable]]:

    if user_input is None or user_input.strip() == "":
        return state, "What is your main business goal?", goal_node

    if not state.current_idea:
        return state, "Error: No idea found. Please restart.", None

    idea = state.current_idea

    if idea not in state.ideas_data:
        state.ideas_data[idea] = {}

    state.ideas_data[idea]["goal"] = user_input

    # Try Gemini
    try:
        summary = ask_gemini(f"Summarize this goal in 3 bullets: {user_input}")
    except Exception as e:
        summary = f"⚠️ Gemini failed to summarize your goal. Reason: {e}"

    msg = (
        f"📌 **Goal Summary for your idea:**\n\n"
        f"{summary}\n\n"
        "Next: Market analysis."
    )

    from src.nodes.market_node import market_node
    return state, msg, market_node
