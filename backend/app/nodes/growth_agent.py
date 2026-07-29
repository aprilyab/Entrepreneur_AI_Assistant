# backend/app/nodes/growth_agent.py
"""Growth Strategist Agent — designs scaling and marketing strategies."""

GROWTH_STRATEGIST_PROMPT = """You are a Growth Strategist specializing in startup scaling.
Design a comprehensive growth strategy for the following startup.

Startup Idea: {idea}
Market Analysis: {market_analysis}
Business Model: {business_model}
Financials: {financials}

Provide your analysis in this EXACT structure:

## Growth Channels
### Primary Channels (Highest ROI)
For each channel:
- **Channel:** [Name]
- **Strategy:** [Specific approach]
- **Expected CAC:** [Cost estimate]
- **Timeline:** [When results expected]

### Secondary Channels (Supporting)
For each channel:
- **Channel:** [Name]
- **Strategy:** [Brief approach]

## Customer Acquisition Strategy
- Launch strategy (first 100 customers)
- Growth loops and viral mechanisms
- Partnership opportunities
- Content marketing plan

## Retention & Engagement
- Onboarding strategy
- Engagement hooks
- Churn reduction tactics
- Community building

## Scaling Roadmap
### Phase 1: Validation (Month 1-3)
- Key metrics to track
- Growth targets
- Required resources

### Phase 2: Growth (Month 3-12)
- Scaling channels
- Team expansion needs
- Infrastructure requirements

### Phase 3: Scale (Year 2-3)
- Market expansion
- Revenue diversification
- Operational scaling

## Key Metrics Dashboard
- North Star Metric
- Leading indicators
- Lagging indicators
- Monthly targets for Year 1

Focus on actionable, data-driven strategies with clear timelines."""


def growth_agent(state: dict) -> dict:
    """LangGraph node: Growth Strategist Agent."""
    from app.services.llm import ask_llm

    prompt = GROWTH_STRATEGIST_PROMPT.format(
        idea=state.get("idea", ""),
        market_analysis=state.get("market_analysis", "Not yet analyzed"),
        business_model=state.get("business_model", "Not yet defined"),
        financials=state.get("financials", "Not yet projected"),
    )
    growth_strategy = ask_llm(prompt)

    return {"growth_strategy": growth_strategy}
