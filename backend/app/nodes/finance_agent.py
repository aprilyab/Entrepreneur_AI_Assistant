# backend/app/nodes/finance_agent.py
"""Finance Expert Agent — builds financial projections and unit economics."""

FINANCE_EXPERT_PROMPT = """You are a senior Finance Expert specializing in startup financials.
Build detailed financial projections for the following startup.

Startup Idea: {idea}
Market Analysis: {market_analysis}
Business Model: {business_model}

Provide your analysis in this EXACT structure:

## Revenue Model
- Primary revenue streams
- Pricing strategy
- Projected monthly revenue (Year 1)

## Cost Structure
- Fixed costs (monthly)
- Variable costs (per unit/customer)
- Total startup costs

## Unit Economics
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- LTV:CAC ratio
- Payback period

## Financial Projections
- Year 1: Monthly revenue, costs, profit
- Year 2: Quarterly projections
- Year 3: Annual projections

## Break-Even Analysis
- Units/customers needed to break even
- Timeline to profitability

## Funding Requirements
- Minimum viable funding
- Recommended seed amount
- Use of funds breakdown

Use realistic numbers. Show your reasoning for key assumptions.

Every numerical metric must also be returned in the structured metrics object.
Do not confuse ARPU with LTV, paid CAC with blended CAC, churn with market growth,
or inference cost with total COGS. Mark every forecast as an assumption unless it
comes from founder-provided historical data. Confidence must reflect evidence quality.
State explicitly whether the LTV:CAC ratio uses paid CAC or blended CAC."""


def finance_agent(state: dict) -> dict:
    """LangGraph node: Finance Expert Agent."""
    from app.schemas.intelligence import FinancialAgentOutput
    from app.services.llm import ask_llm_structured

    prompt = FINANCE_EXPERT_PROMPT.format(
        idea=state.get("idea", ""),
        market_analysis=state.get("market_analysis", "Not yet analyzed"),
        business_model=state.get("business_model", "Not yet defined"),
    )
    output = ask_llm_structured(prompt, FinancialAgentOutput)

    return {
        "financials": output.report_markdown,
        "financial_metrics": output.metrics.model_dump(mode="json"),
    }
