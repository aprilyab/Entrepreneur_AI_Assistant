# backend/app/nodes/plan_agent.py
"""Business Plan Compiler Agent — assembles all sections into a final plan."""

PLAN_COMPILER_PROMPT = """You are a Professional Business Plan Writer.
Compile all the following sections into a polished, investor-ready business plan.

Startup Idea: {idea}
Extra Context: {extra_info}
Approved venture identity: {identity}

--- MARKET ANALYSIS ---
{market_analysis}

--- BUSINESS MODEL ---
{business_model}

--- VALIDATION STRATEGY ---
{validation_strategy}

--- RISK ASSESSMENT ---
{risks}

--- FINANCIAL PROJECTIONS ---
{financials}

--- GROWTH STRATEGY ---
{growth_strategy}

Create a comprehensive business plan with this structure:

# Business Plan: [Company Name]

## 1. Executive Summary
(2-3 paragraph overview that captures the essence of the business)

## 2. Company Description
- Mission statement
- Vision statement
- Legal structure

## 3. Market Analysis
(Summarize key findings from market analysis)

## 4. Products & Services
(What the business offers)

## 5. Business Model
(How the business makes money)

## 6. Marketing & Sales Strategy
(Go-to-market approach)

## 7. Operations Plan
(How the business runs day-to-day)

## 8. Management Team
(Team structure and key roles needed)

## 9. Financial Plan
(Summarize projections, highlight key metrics)

## 10. Risk Analysis
(Top risks and mitigation strategies)

## 11. Funding Requirements
(How much capital is needed and why)

## 12. Implementation Timeline
(Key milestones for first 12 months)

Write in a professional, evidence-aware tone. Use specific numbers from the analysis.
Label all forecasts and targets as projections or assumptions. Describe unbuilt features,
unsigned partnerships, future hires, and planned infrastructure in future tense. Do not turn
generated recommendations into claims of current traction or existing capability.
This should be ready to present to investors or lenders."""


def plan_compiler_agent(state: dict) -> dict:
    """LangGraph node: Business Plan Compiler Agent."""
    from app.services.llm import ask_llm

    prompt = PLAN_COMPILER_PROMPT.format(
        idea=state.get("idea", ""),
        extra_info=state.get("extra_info", ""),
        identity=state.get("identity", {}),
        market_analysis=state.get("market_analysis", ""),
        business_model=state.get("business_model", ""),
        validation_strategy=state.get("validation_strategy", ""),
        risks=state.get("risks", ""),
        financials=state.get("financials", ""),
        growth_strategy=state.get("growth_strategy", ""),
    )
    full_plan = ask_llm(prompt)

    return {"full_plan": full_plan}
