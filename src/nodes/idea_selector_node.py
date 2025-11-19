from typing import Tuple, Optional, Callable
from src.state import EntrepreneurState

VALID_CHOICES = {"online", "offline", "hybrid"}

def idea_selector_node(
    state: EntrepreneurState, 
    user_input: Optional[str] = None
) -> Tuple[EntrepreneurState, str, Optional[Callable]]:

    if user_input is None or user_input.strip() == "":
        return (
            state,
            "Which delivery method do you prefer? (online/offline/hybrid)",
            idea_selector_node
        )

    choice = user_input.strip().lower()

    # validate input
    if choice not in VALID_CHOICES:
        return (
            state,
            "❌ Invalid choice. Please type: online / offline / hybrid.",
            idea_selector_node
        )

    # store choice
    if state.current_idea:
        if state.current_idea not in state.ideas_data:
            state.ideas_data[state.current_idea] = {}
        state.ideas_data[state.current_idea]["delivery"] = choice

    msg = f"Delivery method set to: {choice}. Next, let's define your goal."

    from src.nodes.goal_node import goal_node
    return state, msg, goal_node
