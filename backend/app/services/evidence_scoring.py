"""Evidence-aware confidence adjustment for an AI viability assessment."""


def evidence_adjusted_score(raw_score: int, assumptions: list, evidence: list) -> dict:
    total_evidence = len(evidence)
    linked = sum(1 for item in evidence if getattr(item, "source_url", None))
    verified = sum(1 for item in evidence if getattr(item, "status", "") == "verified")
    total_assumptions = len(assumptions)
    validated = sum(
        1 for item in assumptions if getattr(item, "status", "") == "validated"
    )
    high_untested = sum(
        1
        for item in assumptions
        if getattr(item, "impact", "") == "high"
        and getattr(item, "status", "") in ("untested", "testing")
    )

    linked_ratio = linked / total_evidence if total_evidence else 0
    verified_ratio = verified / total_evidence if total_evidence else 0
    validation_ratio = validated / total_assumptions if total_assumptions else 0
    evidence_confidence = round(
        100 * (0.5 * linked_ratio + 0.3 * verified_ratio + 0.2 * validation_ratio)
    )
    evidence_gap_penalty = round((1 - evidence_confidence / 100) * 15)
    assumption_penalty = min(6, high_untested * 2)
    adjusted = max(0, min(100, raw_score - evidence_gap_penalty - assumption_penalty))

    return {
        "raw_score": raw_score,
        "adjusted_score": adjusted,
        "evidence_confidence": evidence_confidence,
        "linked_claims": linked,
        "total_claims": total_evidence,
        "verified_claims": verified,
        "validated_assumptions": validated,
        "total_assumptions": total_assumptions,
        "high_untested_assumptions": high_untested,
        "penalty": evidence_gap_penalty + assumption_penalty,
        "method": "Raw AI assessment minus evidence-gap and high-impact untested-assumption penalties.",
    }
