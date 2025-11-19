# src/nodes/funding_advisor_node.py
from typing import Tuple, Optional
from src.state import EntrepreneurState
from src.llm.gemini_llm import ask_gemini

def funding_advisor_node(state: EntrepreneurState, user_input: Optional[str] = None) -> Tuple[EntrepreneurState, str, Optional[callable]]:
    idea = state.current_idea
    prompt = f"Summarize funding strategies for: {idea}\nShort bullets only."
    resp = ask_gemini(prompt)
    state.ideas_data[idea]["funding_advice"] = resp
    state.messages.append(resp)

    # Local import
    from src.nodes.validation_node import validation_node
    return state, "Funding advice ready.", validation_node
