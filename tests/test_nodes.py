"""
Test all nodes using EntrepreneurState (Pydantic model) for the updated LangGraph workflow.
"""

from uuid import uuid4
from src.state import EntrepreneurState
from src.nodes.idea_node import idea_node
from src.nodes.idea_selector_node import idea_selector_node
from src.nodes.goal_node import goal_node
from src.nodes.market_node import market_node
from src.nodes.business_model_node import business_model_node
from src.nodes.validation_node import validation_node
from src.nodes.decision_node import decision_node
from src.nodes.risk_node import risk_node
from src.nodes.growth_node import growth_node
from src.nodes.response_node import response_node

# Initialize the state
state = EntrepreneurState(
    session_id=str(uuid4()),
    user_name="Henok",
    consent=True
)

# --- Test Idea Node ---
idea = "I want to build a mini company for recycling with 100,000 ETB initial capital."
state, resp, next_node = idea_node(state)
print("\n--- Idea Node ---")
print(resp)

# --- Test Idea Selector Node ---
state, resp, next_node = idea_selector_node(state)
print("\n--- Idea Selector Node ---")
print(resp)

# --- Test Goal Node ---
state, resp, next_node = goal_node(state)
print("\n--- Goal Node ---")
print(resp)

# Decide next node based on goal/branch
if next_node == market_node:
    state, resp, next_node = market_node(state)
    print("\n--- Market Node ---")
    print(resp)
else:
    state, resp, next_node = business_model_node(state)
    print("\n--- Business Model Node ---")
    print(resp)

# --- Test Validation Node ---
state, resp, next_node = validation_node(state)
print("\n--- Validation Node ---")
print(resp)

# --- Test Decision Node ---
state, resp, next_node = decision_node(state)
print("\n--- Decision Node ---")
print(resp)

# --- Test Risk or Growth Node depending on choice ---
if next_node == risk_node:
    state, resp, next_node = risk_node(state)
    print("\n--- Risk Node ---")
    print(resp)
else:
    state, resp, next_node = growth_node(state)
    print("\n--- Growth Node ---")
    print(resp)

# --- Test Response Node ---
state, final_output, _ = response_node(state)
print("\n--- Response Node ---")
print(final_output)

print("\nAll nodes tested successfully!")
