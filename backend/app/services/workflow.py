# backend/app/services/workflow.py
"""
LangGraph Multi-Agent Workflow for Business Plan Generation.

Architecture: Supervisor Pattern
- Supervisor routes to specialized agents
- Each agent works on its domain
- Results accumulate in shared state
- Plan compiler assembles final output
"""
from typing import Callable, TypedDict
from langgraph.graph import StateGraph, END


class AgentState(TypedDict, total=False):
    """Shared state flowing through the multi-agent graph."""
    idea: str
    extra_info: str
    market_analysis: str
    business_model: str
    validation_strategy: str
    risks: str
    financials: str
    financial_metrics: dict
    contradiction_issues: list[dict]
    consistency_issues: list[dict]
    identity: dict
    capability_claims: list[dict]
    validation_experiments: list[dict]
    growth_strategy: str
    research_sources: list[dict]
    viability_score: int
    full_plan: str
    current_agent: str
    completed_agents: list[str]


class WorkflowCancelled(RuntimeError):
    """Raised when a persisted generation job requests cancellation."""


def supervisor(state: AgentState) -> dict:
    """
    Supervisor node: decides which agent should work next.
    Routes through all agents in order, then to plan compiler.
    """
    completed = state.get("completed_agents", [])

    # Sequential routing through all agents
    agent_order = [
        "market", "identity", "strategy", "capabilities", "finance", "check_finance", "risk", "growth", "validate", "audit", "compile"
    ]

    for agent in agent_order:
        if agent not in completed:
            return {"current_agent": agent}

    # All agents completed
    return {"current_agent": "FINISH"}


def route_from_supervisor(state: AgentState) -> str:
    """Conditional edge: route to the next agent or finish."""
    current = state.get("current_agent", "FINISH")
    if current == "FINISH":
        return "end"
    return current


def build_workflow() -> StateGraph:
    """
    Build the LangGraph multi-agent workflow.

    Flow:
    supervisor → market → identity → strategy → capabilities → finance
               → financial check → risk → growth → validation → audit
               → compilation → END
    """
    from app.nodes import (
        market_agent,
        strategy_agent,
        risk_agent,
        finance_agent,
        growth_agent,
        validation_agent,
        plan_compiler_agent,
        audit_agent,
        financial_check_node,
        identity_agent,
        capability_agent,
    )

    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("supervisor", supervisor)
    graph.add_node("market", market_agent)
    graph.add_node("strategy", strategy_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("finance", finance_agent)
    graph.add_node("growth", growth_agent)
    graph.add_node("validate", validation_agent)
    graph.add_node("compile", plan_compiler_agent)
    graph.add_node("audit", audit_agent)
    graph.add_node("check_finance", financial_check_node)
    graph.add_node("identity", identity_agent)
    graph.add_node("capabilities", capability_agent)

    # Helper: after each agent, mark it completed and return to supervisor
    def make_return_to_supervisor(agent_name: str):
        def handler(state: AgentState) -> dict:
            completed = state.get("completed_agents", [])
            return {"completed_agents": completed + [agent_name]}
        return handler

    for agent_name in ["market", "identity", "strategy", "capabilities", "risk", "finance", "check_finance", "growth", "validate", "audit"]:
        return_node = f"return_{agent_name}"
        graph.add_node(return_node, make_return_to_supervisor(agent_name))
        graph.add_edge(agent_name, return_node)
        graph.add_edge(return_node, "supervisor")

    # After compile, go to end
    graph.add_edge("compile", END)

    # Supervisor routes conditionally
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "market": "market",
            "strategy": "strategy",
            "risk": "risk",
            "finance": "finance",
            "growth": "growth",
            "validate": "validate",
            "compile": "compile",
            "audit": "audit",
            "check_finance": "check_finance",
            "identity": "identity",
            "capabilities": "capabilities",
            "end": END,
        },
    )

    # Entry point
    graph.set_entry_point("supervisor")

    return graph


# Compile the workflow once at module load
_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow().compile()
    return _workflow


def run_business_plan_workflow(
    idea: str,
    extra_info: str = "",
    *,
    saved_state: dict | None = None,
    progress_callback: Callable[[str, dict], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> dict:
    """
    Execute the full multi-agent business plan workflow.

    Returns:
        dict with all agent outputs and the final plan.
    """
    workflow = get_workflow()

    initial_state: AgentState = {
        "idea": idea,
        "extra_info": extra_info,
        "market_analysis": "",
        "business_model": "",
        "validation_strategy": "",
        "risks": "",
        "financials": "",
        "financial_metrics": {},
        "contradiction_issues": [],
        "consistency_issues": [],
        "identity": {},
        "capability_claims": [],
        "validation_experiments": [],
        "growth_strategy": "",
        "research_sources": [],
        "viability_score": 0,
        "full_plan": "",
        "current_agent": "",
        "completed_agents": [],
    }
    if saved_state:
        initial_state.update(saved_state)
        initial_state["idea"] = idea
        initial_state["extra_info"] = extra_info
        initial_state["current_agent"] = ""

    result: dict = dict(initial_state)
    if cancel_check and cancel_check():
        raise WorkflowCancelled("Generation cancelled before execution.")

    for update in workflow.stream(initial_state, stream_mode="updates"):
        for node_name, values in update.items():
            if isinstance(values, dict):
                result.update(values)
            if progress_callback:
                progress_callback(node_name, dict(result))
            if (
                cancel_check
                and (node_name == "supervisor" or node_name.startswith("return_"))
                and cancel_check()
            ):
                raise WorkflowCancelled("Generation cancelled by user.")

    return {
        "idea": result.get("idea", idea),
        "extra_info": result.get("extra_info", extra_info),
        "market_analysis": result.get("market_analysis", ""),
        "business_model": result.get("business_model", ""),
        "validation_strategy": result.get("validation_strategy", ""),
        "risks": result.get("risks", ""),
        "financials": result.get("financials", ""),
        "financial_metrics": result.get("financial_metrics", {}),
        "contradiction_issues": result.get("contradiction_issues", []),
        "consistency_issues": result.get("consistency_issues", []),
        "identity": result.get("identity", {}),
        "capability_claims": result.get("capability_claims", []),
        "validation_experiments": result.get("validation_experiments", []),
        "growth_strategy": result.get("growth_strategy", ""),
        "research_sources": result.get("research_sources", []),
        "viability_score": result.get("viability_score", 0),
        "full_plan": result.get("full_plan", ""),
    }
