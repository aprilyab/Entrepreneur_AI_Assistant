from langgraph.graph import StateGraph, END
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


def build_graph():
    builder = StateGraph(EntrepreneurState)

    # --- Add all nodes ---
    builder.add_node("idea", idea_node)
    builder.add_node("selector", idea_selector_node)
    builder.add_node("goal", goal_node)
    builder.add_node("market", market_node)
    builder.add_node("business_model", business_model_node)
    builder.add_node("validation", validation_node)
    builder.add_node("decision", decision_node)
    builder.add_node("risk", risk_node)
    builder.add_node("growth", growth_node)
    builder.add_node("response", response_node)

    # --- Set entry point ---
    builder.set_entry_point("idea")

    # --- Main workflow edges ---
    builder.add_edge("idea", "selector")
    builder.add_edge("selector", "goal")

    # Replace conditional edges
    builder.add_conditional_edges(
        "goal",
        lambda state: "market" if getattr(state, "branch_to_market", True) else "business_model",
        path_map={"market": "market", "business_model": "business_model"},
    )

    builder.add_edge("market", "validation")
    builder.add_edge("business_model", "validation")
    builder.add_edge("validation", "decision")

    # Branching after decision
    builder.add_conditional_edges(
        "decision",
        lambda state: "risk" if getattr(state, "go_to_risk", True) else "growth",
        path_map={"risk": "risk", "growth": "growth"},
    )

    builder.add_edge("risk", "response")
    builder.add_edge("growth", "response")

    # End node
    builder.add_edge("response", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    graph.get_graph().draw_png("entrepreneur_graph.png")
