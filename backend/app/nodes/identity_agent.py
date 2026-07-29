"""Generate a concise venture identity instead of echoing the founder prompt."""

IDENTITY_PROMPT = """Act as a senior startup naming strategist.
Create a concise identity for this venture:

Idea: {idea}
Context: {extra_info}
Market context: {market_analysis}

Requirements:
- Name: distinctive, pronounceable, 1-2 words, maximum 20 visible characters.
- Avoid generic suffixes such as AI, GPT, Pilot, Hub, Studio, Labs, or Solutions.
- Do not merely repeat the founder's input sentence.
- Subtitle: plain-English category description, not a slogan.
- One-liner: target customer + outcome + differentiator.
- Give up to four materially different alternative names.
- Do not claim trademark or domain availability.
"""


def identity_agent(state: dict) -> dict:
    from app.schemas.intelligence import VentureIdentity
    from app.services.llm import ask_llm_structured

    identity = ask_llm_structured(
        IDENTITY_PROMPT.format(
            idea=state.get("idea", ""),
            extra_info=state.get("extra_info", "") or "None provided",
            market_analysis=state.get("market_analysis", ""),
        ),
        VentureIdentity,
    )
    return {"identity": identity.model_dump(mode="json")}
