"""Deterministic arithmetic checks for structured financial projections."""

from __future__ import annotations


def _value(metrics: dict, name: str) -> float | None:
    item = metrics.get(name)
    if not isinstance(item, dict):
        return None
    value = item.get("value")
    return float(value) if isinstance(value, (int, float)) else None


def _issue(code: str, severity: str, message: str, expected: str, actual: str) -> dict:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "expected": expected,
        "actual": actual,
    }


def check_financial_consistency(metrics: dict) -> list[dict]:
    """Return reproducible problems without asking an LLM to do arithmetic."""
    issues: list[dict] = []
    allocations = metrics.get("use_of_funds") or []
    if allocations:
        percentage_total = sum(float(item.get("percentage", 0)) for item in allocations)
        if abs(percentage_total - 100) > 0.5:
            issues.append(
                _issue(
                    "allocation_percentage_total",
                    "high",
                    "Use-of-funds percentages do not total 100%.",
                    "100%",
                    f"{percentage_total:.1f}%",
                )
            )
        recommended = _value(metrics, "recommended_funding")
        amount_total = sum(float(item.get("amount", 0)) for item in allocations)
        if recommended and abs(amount_total - recommended) / recommended > 0.02:
            issues.append(
                _issue(
                    "allocation_amount_total",
                    "high",
                    "Use-of-funds amounts do not match the recommended raise.",
                    f"{recommended:,.0f}",
                    f"{amount_total:,.0f}",
                )
            )

    minimum = _value(metrics, "minimum_funding")
    recommended = _value(metrics, "recommended_funding")
    if minimum is not None and recommended is not None and minimum > recommended:
        issues.append(
            _issue(
                "funding_order",
                "high",
                "Minimum viable funding exceeds the recommended funding target.",
                "minimum ≤ recommended",
                f"{minimum:,.0f} > {recommended:,.0f}",
            )
        )

    ltv = _value(metrics, "ltv")
    ratio = _value(metrics, "ltv_cac_ratio")
    denominator_name = metrics.get("ltv_cac_denominator")
    cac = _value(metrics, denominator_name) if denominator_name else None
    if ltv is not None and cac and ratio is not None:
        expected_ratio = ltv / cac
        if abs(expected_ratio - ratio) / max(expected_ratio, 0.01) > 0.05:
            issues.append(
                _issue(
                    "ltv_cac_math",
                    "critical",
                    "The reported LTV:CAC ratio does not match its selected CAC denominator.",
                    f"{expected_ratio:.2f}:1",
                    f"{ratio:.2f}:1",
                )
            )

    arpu = _value(metrics, "arpu")
    margin = _value(metrics, "gross_margin_rate")
    churn = _value(metrics, "monthly_churn_rate")
    if arpu and margin is not None and churn and ltv is not None:
        margin_decimal = margin / 100 if margin > 1 else margin
        churn_decimal = churn / 100 if churn > 1 else churn
        expected_ltv = arpu * margin_decimal / churn_decimal
        if abs(expected_ltv - ltv) / max(expected_ltv, 0.01) > 0.1:
            issues.append(
                _issue(
                    "ltv_math",
                    "high",
                    "LTV is inconsistent with ARPU, gross margin, and monthly churn.",
                    f"{expected_ltv:,.2f}",
                    f"{ltv:,.2f}",
                )
            )

    return issues
