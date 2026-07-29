"""Classify product and traction claims by their actual maturity."""

CAPABILITY_PROMPT = """Audit the venture below and classify its most important product,
traction, partnership, and operational claims.

Founder brief:
{idea}
{extra_info}

Generated business model:
{business_model}

Rules:
- "existing" only when the founder brief explicitly says it is built, launched, signed,
  measured, or already operating.
- "proposed" for features, partnerships, integrations, teams, or systems the plan recommends.
- "assumption" for forecasts, targets, performance expectations, and unverified outcomes.
- Never infer that a generated recommendation already exists.
- Return 5-12 concise claims and cite the sentence or absence of founder evidence.
"""


def capability_agent(state: dict) -> dict:
    from app.schemas.intelligence import CapabilityAuditOutput
    from app.services.llm import ask_llm_structured

    output = ask_llm_structured(
        CAPABILITY_PROMPT.format(
            idea=state.get("idea", ""),
            extra_info=state.get("extra_info", "") or "No additional founder evidence.",
            business_model=state.get("business_model", ""),
        ),
        CapabilityAuditOutput,
    )
    return {
        "capability_claims": [
            claim.model_dump(mode="json") for claim in output.claims
        ]
    }
