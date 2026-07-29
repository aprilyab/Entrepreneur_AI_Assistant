# backend/app/nodes/strategy_agent.py
"""Strategy Advisor Agent — creates business models and strategic positioning."""

STRATEGY_ADVISOR_PROMPT = """You are a Strategy Advisor specializing in startup business models.
Design a comprehensive business model for the following startup idea.

Startup Idea: {idea}
Market Analysis: {market_analysis}
Additional Context: {extra_info}

Provide your analysis in this EXACT structure:

## Value Proposition
- Core problem solved
- Unique value delivered
- Key differentiators

## Business Model Canvas
- Key Partners
- Key Activities
- Key Resources
- Value Propositions
- Customer Relationships
- Channels
- Customer Segments
- Cost Structure
- Revenue Streams

## Go-to-Market Strategy
- Launch strategy (first 90 days)
- Marketing channels
- Pricing strategy
- Sales approach

## Competitive Moat
- Defensibility of the business
- Network effects potential
- Barriers to entry for competitors

## Scalability Plan
- Phase 1: MVP (0-6 months)
- Phase 2: Growth (6-18 months)
- Phase 3: Scale (18-36 months)

Be specific and actionable. Focus on what makes this business unique and investable.
Use future tense for every unbuilt feature, unsigned partnership, unverified moat, and
planned hire. Clearly label numerical targets as founder assumptions or projections."""


def strategy_agent(state: dict) -> dict:
    """LangGraph node: Strategy Advisor Agent."""
    from app.services.llm import ask_llm

    prompt = STRATEGY_ADVISOR_PROMPT.format(
        idea=state.get("idea", ""),
        market_analysis=state.get("market_analysis", "Not yet analyzed"),
        extra_info=state.get("extra_info", "None provided"),
    )
    business_model = ask_llm(prompt)

    return {"business_model": business_model}
