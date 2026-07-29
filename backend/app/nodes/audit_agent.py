"""Cross-section audit agent for detecting internally inconsistent claims."""

AUDIT_PROMPT = """You are a meticulous startup investment-committee analyst.
Audit the generated venture reports below for contradictions between sections.

Only report genuine contradictions: two claims that cannot both be true, use different
values for the same metric or target, promise a capability that another section says is
unavailable, or give incompatible timing/customer/financial assumptions.

Do not report ordinary uncertainty, missing evidence, different levels of detail, or
minor rounding differences below 2%. Quote each conflicting claim concisely, name its
source section, explain the conflict, and recommend one concrete resolution.
Return an empty issues list when the reports are internally consistent.

IDEA
{idea}

MARKET ANALYSIS
{market_analysis}

BUSINESS MODEL
{business_model}

FINANCIALS
{financials}

RISKS
{risks}

GROWTH STRATEGY
{growth_strategy}

VALIDATION REPORT
{validation_strategy}
"""


def audit_agent(state: dict) -> dict:
    from app.schemas.intelligence import ContradictionAuditOutput
    from app.services.llm import ask_llm_structured

    output = ask_llm_structured(
        AUDIT_PROMPT.format(
            idea=state.get("idea", ""),
            market_analysis=state.get("market_analysis", ""),
            business_model=state.get("business_model", ""),
            financials=state.get("financials", ""),
            risks=state.get("risks", ""),
            growth_strategy=state.get("growth_strategy", ""),
            validation_strategy=state.get("validation_strategy", ""),
        ),
        ContradictionAuditOutput,
    )
    return {
        "contradiction_issues": [
            issue.model_dump(mode="json") for issue in output.issues
        ]
    }
