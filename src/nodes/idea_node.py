from typing import Tuple, Optional
from src.state import EntrepreneurState

def idea_node(state: EntrepreneurState, user_text: Optional[str] = None) -> Tuple[EntrepreneurState, str, Optional[callable]]:
    if user_text is None or user_text.strip() == "":
        return state, "Please describe your startup idea.", idea_node

    state.messages.append(user_text)
    state.current_idea = user_text
    if user_text not in state.ideas:
        state.ideas.append(user_text)
        state.ideas_data[user_text] = {}

    prompt = f"Great! Your idea is: {user_text}. Let me analyze and ask further questions if needed."

    from src.nodes.market_node import market_node
    return state, prompt, market_node
