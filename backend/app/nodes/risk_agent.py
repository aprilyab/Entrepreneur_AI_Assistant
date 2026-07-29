# backend/app/nodes/risk_agent.py
"""Risk Analyzer Agent — identifies risks and mitigation strategies."""

RISK_ANALYZER_PROMPT = """You are a Risk Analysis Expert for startups.
Identify and analyze all potential risks for the following startup.

Startup Idea: {idea}
Market Analysis: {market_analysis}
Business Model: {business_model}
Financials: {financials}

Provide your analysis in this EXACT structure:

## Risk Assessment Matrix

### Critical Risks (Score: 8-10)
For each critical risk:
- **Risk:** [Description]
- **Impact:** [Financial/Operational/Reputational]
- **Probability:** [Low/Medium/High]
- **Mitigation:** [Specific action to mitigate]

### High Risks (Score: 5-7)
For each high risk:
- **Risk:** [Description]
- **Impact:** [Financial/Operational/Reputational]
- **Probability:** [Low/Medium/High]
- **Mitigation:** [Specific action to mitigate]

### Medium Risks (Score: 2-4)
For each medium risk:
- **Risk:** [Description]
- **Mitigation:** [Brief action]

## SWOT Analysis
- **Strengths:** Internal advantages
- **Weaknesses:** Internal challenges
- **Opportunities:** External favorable conditions
- **Threats:** External challenges

## Regulatory & Compliance Risks
- Required licenses/permits
- Industry regulations
- Data privacy considerations

## Risk Mitigation Timeline
- Immediate actions (Week 1-4)
- Short-term actions (Month 1-3)
- Long-term monitoring (Month 3-12)

Be thorough and realistic. Prioritize risks by potential impact."""


def risk_agent(state: dict) -> dict:
    """LangGraph node: Risk Analyzer Agent."""
    from app.services.llm import ask_llm

    prompt = RISK_ANALYZER_PROMPT.format(
        idea=state.get("idea", ""),
        market_analysis=state.get("market_analysis", "Not yet analyzed"),
        business_model=state.get("business_model", "Not yet defined"),
        financials=state.get("financials", "Not yet projected"),
    )
    risks = ask_llm(prompt)

    return {"risks": risks}
