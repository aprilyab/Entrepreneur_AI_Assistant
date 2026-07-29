# backend/app/nodes/market_agent.py
"""Market Analyst Agent — researches market size, trends, competitors."""

MARKET_ANALYST_PROMPT = """You are an expert Market Analyst for startups.
Analyze the following startup idea and provide a comprehensive market analysis.

Startup Idea: {idea}
Additional Context: {extra_info}

Provide your analysis in this EXACT structure:

## Market Overview
- Market size (TAM/SAM/SOM estimates)
- Growth rate and trends
- Key market drivers

## Target Customers
- Primary customer segments
- Customer pain points
- Buying behavior

## Competitive Landscape
- Top 5 competitors (name, funding, positioning)
- Competitor strengths and weaknesses
- Market gaps and opportunities

## Industry Trends
- Technology trends affecting this market
- Regulatory considerations
- Emerging opportunities

Be specific with numbers and data where possible. If exact data is unavailable, provide reasonable estimates based on industry knowledge."""


def market_agent(state: dict) -> dict:
    """LangGraph node: Market Analyst Agent."""
    from app.services.grounded_research import grounded_market_analysis
    from app.services.llm import ask_llm

    idea = state.get("idea", "")
    extra_info = state.get("extra_info", "")

    analysis, sources = grounded_market_analysis(idea, extra_info)
    if not analysis:
        prompt = MARKET_ANALYST_PROMPT.format(idea=idea, extra_info=extra_info or "None provided")
        analysis = ask_llm(prompt)

    return {"market_analysis": analysis, "research_sources": sources}
