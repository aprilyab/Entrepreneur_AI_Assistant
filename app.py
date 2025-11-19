# app.py
import streamlit as st
import uuid
from typing import Optional, Callable, Tuple

from src.state import EntrepreneurState
from src.nodes.idea_node import idea_node
from src.nodes.idea_selector_node import idea_selector_node
from src.nodes.goal_node import goal_node
from src.nodes.market_node import market_node
from src.nodes.business_model_node import business_model_node
from src.nodes.validation_node import validation_node
from src.nodes.risk_node import risk_node
from src.nodes.growth_node import growth_node
from src.nodes.response_node import response_node

# -------------------------------
# Node flow order
# -------------------------------
NODE_FLOW = [
    idea_node,
    idea_selector_node,
    goal_node,
    market_node,
    business_model_node,
    validation_node,
    risk_node,
    growth_node,
    response_node
]

# -------------------------------
# Initialize session state
# -------------------------------
if "graph_state" not in st.session_state:
    st.session_state.graph_state = EntrepreneurState(
        session_id=str(uuid.uuid4()),
        user_name=None,
        consent=True
    )
    st.session_state.current_node: Optional[Callable] = idea_node
    st.session_state.chat_history = []

st.title("🚀 Entrepreneur AI Assistant")
st.write("Chat with an AI agent that builds your startup plan step-by-step.")

# -------------------------------
# Helper function to run a node safely
# -------------------------------
def run_node(node_func, state, user_input):
    try:
        return node_func(state, user_input)
    except Exception as e:
        node_name = getattr(node_func, "__name__", "unknown_node")
        return (
            state,
            f"⚠️ Error in node {node_name}: {e}",
            None
        )

# -------------------------------
# Display chat history
# -------------------------------
for msg in st.session_state.chat_history:
    st.markdown(msg)

# -------------------------------
# User input
# -------------------------------
user_input = st.chat_input("Type your message...")

if user_input or st.session_state.current_node:
    node_func = st.session_state.current_node
    state = st.session_state.graph_state

    state, output, next_node = run_node(node_func, state, user_input)

    # Save chat messages
    if user_input:
        st.session_state.chat_history.append(f"**You:** {user_input}")
    st.session_state.chat_history.append(f"**Assistant:** {output}")

    # Update state and next node
    st.session_state.graph_state = state
    st.session_state.current_node = next_node

    # Clear input box
    st.session_state.input_box = ""

    # If workflow completed
    if next_node is None:
        st.session_state.chat_history.append("✅ Workflow completed! You have your startup plan.")

    st.stop()

# -------------------------------
# Debug / Internal state
# -------------------------------
st.write("---")
st.subheader("🧠 Internal State (Debug)")
st.json(st.session_state.graph_state.model_dump())  # Pydantic V2 compatible
