# backend/app/nodes/validation_agent.py
"""Validator Agent — scores idea viability and suggests validation steps."""

VALIDATOR_PROMPT = """You are a Startup Validator and Idea Scoring Expert.
Evaluate the viability of the following startup idea across multiple dimensions.

Startup Idea: {idea}
Market Analysis: {market_analysis}
Business Model: {business_model}
Financials: {financials}
Risks: {risks}

Provide your evaluation in this EXACT JSON-like structure (but as formatted text):

## Viability Score: [XX]/100

### Verdict: [STRONG GO / PROMISING / NEEDS WORK / RETHINK]

### Score Breakdown
- **Market Demand:** [XX]/25 — [Reasoning]
- **Competition Intensity:** [XX]/20 — [Reasoning]
- **Feasibility:** [XX]/20 — [Reasoning]
- **Profitability Potential:** [XX]/15 — [Reasoning]
- **Timing:** [XX]/10 — [Reasoning]
- **Execution Risk:** [XX]/10 — [Reasoning]

### Green Flags (Strengths)
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### Red Flags (Concerns)
1. [Concern 1]
2. [Concern 2]
3. [Concern 3]

### Validation Recommendations
1. [Actionable validation step 1]
2. [Actionable validation step 2]
3. [Actionable validation step 3]

### Next Steps
1. [Immediate next step]
2. [Short-term action]
3. [Medium-term goal]

Be honest and constructive. A score above 70 means proceed with confidence.
50-70 means promising but needs refinement. Below 50 means significant concerns.

Also return 3-5 structured validation experiments. Each experiment must test one
high-impact assumption, have a bounded method, a realistic budget, and a numeric
pass/fail threshold (for example "at least 8 of 15 interviews" or ">= 10% conversion").
Never use placeholder text such as "define a metric later"."""


def validation_agent(state: dict) -> dict:
    """LangGraph node: Validator Agent."""
    from app.schemas.intelligence import ValidationAgentOutput
    from app.services.llm import ask_llm_structured

    prompt = VALIDATOR_PROMPT.format(
        idea=state.get("idea", ""),
        market_analysis=state.get("market_analysis", "Not yet analyzed"),
        business_model=state.get("business_model", "Not yet defined"),
        financials=state.get("financials", "Not yet projected"),
        risks=state.get("risks", "Not yet assessed"),
    )
    output = ask_llm_structured(prompt, ValidationAgentOutput)

    return {
        "validation_strategy": output.report_markdown,
        "viability_score": output.viability_score,
        "validation_experiments": [
            experiment.model_dump(mode="json") for experiment in output.experiments
        ],
    }
