"""Fast checks for the non-LLM decision logic.

This script intentionally avoids network calls and a database connection. It is the
minimum confidence gate to run before the slower authenticated and live-AI smoke tests.
"""

from types import SimpleNamespace

from app.services.evidence_scoring import evidence_adjusted_score
from app.services.financial_consistency import check_financial_consistency


def metric(value: float) -> dict:
    return {"value": value}


def check_consistent_financials() -> None:
    metrics = {
        "recommended_funding": metric(500_000),
        "minimum_funding": metric(250_000),
        "ltv": metric(300),
        "blended_cac": metric(100),
        "ltv_cac_ratio": metric(3),
        "ltv_cac_denominator": "blended_cac",
        "arpu": metric(50),
        "gross_margin_rate": metric(60),
        "monthly_churn_rate": metric(10),
        "use_of_funds": [
            {"category": "Product", "percentage": 60, "amount": 300_000},
            {"category": "Growth", "percentage": 40, "amount": 200_000},
        ],
    }
    assert check_financial_consistency(metrics) == []


def check_inconsistent_financials() -> None:
    metrics = {
        "recommended_funding": metric(400_000),
        "minimum_funding": metric(500_000),
        "ltv": metric(300),
        "blended_cac": metric(100),
        "ltv_cac_ratio": metric(9),
        "ltv_cac_denominator": "blended_cac",
        "use_of_funds": [
            {"category": "Product", "percentage": 70, "amount": 100_000},
            {"category": "Growth", "percentage": 20, "amount": 100_000},
        ],
    }
    codes = {item["code"] for item in check_financial_consistency(metrics)}
    assert {
        "allocation_percentage_total",
        "allocation_amount_total",
        "funding_order",
        "ltv_cac_math",
    }.issubset(codes)


def check_evidence_adjustment() -> None:
    assumptions = [
        SimpleNamespace(status="untested", impact="high"),
        SimpleNamespace(status="validated", impact="medium"),
    ]
    evidence = [
        SimpleNamespace(source_url="https://example.com/a", status="verified"),
        SimpleNamespace(source_url="https://example.com/b", status="unverified"),
    ]
    result = evidence_adjusted_score(80, assumptions, evidence)
    assert result["raw_score"] == 80
    assert result["adjusted_score"] < result["raw_score"]
    assert result["evidence_confidence"] == 75
    assert result["verified_claims"] == 1
    assert result["validated_assumptions"] == 1


if __name__ == "__main__":
    check_consistent_financials()
    check_inconsistent_financials()
    check_evidence_adjustment()
    print(
        {
            "status": "passed",
            "financial_consistency": True,
            "evidence_adjustment": True,
            "network_calls": 0,
        }
    )
