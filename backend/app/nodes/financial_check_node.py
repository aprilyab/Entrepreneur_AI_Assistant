"""Deterministic financial audit node."""


def financial_check_node(state: dict) -> dict:
    from app.services.financial_consistency import check_financial_consistency

    return {
        "consistency_issues": check_financial_consistency(
            state.get("financial_metrics", {})
        )
    }
