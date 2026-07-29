"""Create a structured validation workspace from generated plan narratives."""

import re

from app.models.plan import EvidenceClaim, PlanAssumption, ValidationExperiment


ASSUMPTION_PATTERNS = [
    ("TAM", "market", "high", r"\bTAM\b[^$\n]{0,80}(\$[\d,.]+\s*(?:billion|million|[BMK])?)"),
    ("SAM", "market", "high", r"\bSAM\b[^$\n]{0,80}(\$[\d,.]+\s*(?:billion|million|[BMK])?)"),
    ("SOM", "market", "high", r"\bSOM\b[^$\n]{0,80}(\$[\d,.]+\s*(?:billion|million|[BMK])?)"),
    ("Growth rate", "market", "medium", r"(?:CAGR|growth rate)[^%\n]{0,80}([\d.]+\s*%)"),
    ("Selling price", "financial", "high", r"(?:MSRP|single unit|selling price)[^$\n]{0,80}(\$[\d,.]+)"),
    ("Cost of goods", "financial", "high", r"\bCOGS\b[^$\n]{0,80}(\$[\d,.]+)"),
    ("Customer acquisition cost", "financial", "high", r"\bCAC\b[^$\n]{0,80}(\$[\d,.]+)"),
    ("Customer lifetime value", "financial", "high", r"\bLTV\b[^$\n]{0,80}(\$[\d,.]+)"),
]


def _clean_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`#]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -:\n\t")


def build_assumptions(
    plan,
    financial_metrics: dict | None = None,
) -> list[PlanAssumption]:
    content = "\n".join([plan.market_analysis or "", plan.financials or "", plan.business_model or ""])
    assumptions: list[PlanAssumption] = []
    for name, category, impact, pattern in ASSUMPTION_PATTERNS:
        if financial_metrics and category == "financial":
            continue
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            assumptions.append(
                PlanAssumption(
                    plan_id=plan.id,
                    name=name,
                    value=_clean_markdown(match.group(1)),
                    category=category,
                    impact=impact,
                    confidence=25,
                    source_type="ai_estimate",
                    status="untested",
                    validation_method="Replace this estimate with founder data or verified external evidence.",
                )
            )

    for item in (financial_metrics or {}).get("assumptions", []):
        assumptions.append(
            PlanAssumption(
                plan_id=plan.id,
                name=item.get("name", "Financial assumption")[:250],
                value=item.get("value", "Not provided")[:250],
                category="financial",
                source_type="ai_estimate",
                confidence=max(0, min(100, int(item.get("confidence", 20)))),
                impact=item.get("impact", "medium"),
                status="untested",
                validation_method=item.get(
                    "validation_method",
                    "Replace this forecast with observed founder data.",
                ),
            )
        )
    if not assumptions:
        assumptions = [
            PlanAssumption(
                plan_id=plan.id,
                name="Target customer's willingness to pay",
                value="Not validated",
                category="customer",
                impact="high",
                confidence=10,
                validation_method="Run pricing interviews with at least 10 target customers.",
            ),
            PlanAssumption(
                plan_id=plan.id,
                name="Customer acquisition channel",
                value="Not validated",
                category="growth",
                impact="high",
                confidence=10,
                validation_method="Test one channel with a fixed budget and conversion threshold.",
            ),
        ]
    return assumptions


def _claim_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _strip_report_label(value: str) -> str:
    return re.sub(
        r"^(?:supported\s+market\s+size\s+and\s+growth\s+claims|"
        r"positioning\s+and\s+pricing\s+only\s+when\s+supported|"
        r"supported\s+pricing\s+claims)\s*:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    ).strip()


def _citation_ids(line: str) -> list[str]:
    ids: list[str] = []
    for label in re.findall(r"\[([^\]]*S\d+[^\]]*)\]", line, re.IGNORECASE):
        ids.extend(re.findall(r"S\d+", label, re.IGNORECASE))
    return list(dict.fromkeys(item.upper() for item in ids))


def _is_report_claim(line: str, *, in_source_index: bool) -> bool:
    raw = line.strip()
    if not raw or in_source_index or raw.startswith("#"):
        return False
    if re.match(r"^\s*\[?S\d+\s*[—:-]", raw, re.IGNORECASE):
        return False
    cleaned = _clean_markdown(re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw))
    if len(cleaned) < 35 or len(cleaned) > 900:
        return False
    generic = {
        "supported market size and growth claims",
        "tam sam som with assumptions explicitly labeled",
        "named competitors found in the packet",
        "positioning and pricing only when supported",
        "source coverage summary",
        "important evidence gaps",
    }
    return _claim_key(cleaned) not in {_claim_key(item) for item in generic}


def build_evidence_claims(plan, research_sources: list[dict] | None = None) -> list[EvidenceClaim]:
    """Build one deduplicated evidence record per report claim, linked to its cited source."""
    claims: list[EvidenceClaim] = []
    seen: set[str] = set()
    sources = research_sources or []
    source_by_id = {str(source.get("id", "")).upper(): source for source in sources}
    source_by_url = {source.get("url"): source for source in sources if source.get("url")}
    signal = re.compile(
        r"(?:\$[\d,.]+|[\d.]+\s*%|CAGR|market size|regulation|standard|competitor|funding)",
        re.IGNORECASE,
    )
    in_source_index = False
    unlinked_count = 0
    for line in (plan.market_analysis or "").splitlines():
        if re.match(r"^#{1,4}\s+Source Index\b", line.strip(), re.IGNORECASE):
            in_source_index = True
            continue
        if not _is_report_claim(line, in_source_index=in_source_index):
            continue

        raw_urls = re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", line)
        cited_sources = [
            source_by_id[item]
            for item in _citation_ids(line)
            if item in source_by_id
        ]
        cited_sources.extend(
            source_by_url[url]
            for url in raw_urls
            if url in source_by_url and source_by_url[url] not in cited_sources
        )
        cited_sources.sort(key=lambda item: int(item.get("confidence", 0)), reverse=True)

        without_citations = re.sub(r"\s*\[[^\]]*S\d+[^\]]*\](?:\([^)]+\))?", "", line, flags=re.IGNORECASE)
        claim = _strip_report_label(
            _clean_markdown(
                re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", without_citations)
            )
        )
        if re.match(r"^(?:founder\s+)?assumption\b", claim, re.IGNORECASE):
            continue
        key = _claim_key(claim)
        if key in seen:
            continue
        if not cited_sources and not signal.search(claim):
            continue
        if not cited_sources:
            unlinked_count += 1
            if unlinked_count > 3:
                continue
        seen.add(key)
        primary = cited_sources[0] if cited_sources else {}
        additional = cited_sources[1:]
        notes = (
            "[auto:cited-claim] Generated from a cited market-report claim. "
            "Open the source and confirm that it supports the complete claim before verification."
            if primary
            else "[auto:unlinked-claim] Quantitative or decision-relevant report claim with no attached source."
        )
        if additional:
            notes += " Additional cited sources: " + ", ".join(
                f"{item.get('id')}: {item.get('url')}" for item in additional
            )
        claims.append(
            EvidenceClaim(
                plan_id=plan.id,
                claim=claim[:1000],
                source_title=(primary.get("title") or "")[:500] or None,
                source_url=primary.get("url"),
                status="sourced" if primary else "unverified",
                confidence=max(
                    0,
                    min(100, int(primary.get("confidence", 20) if primary else 20)),
                ),
                notes=notes,
            )
        )
        if len(claims) == 12:
            break
    return claims


def _recommendation_lines(content: str) -> list[str]:
    section = re.search(
        r"Validation Recommendations(.*?)(?:\n#{2,3}\s+Next Steps|\Z)",
        content or "",
        re.IGNORECASE | re.DOTALL,
    )
    if not section:
        return []
    results = []
    for line in section.group(1).splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        cleaned = _clean_markdown(cleaned)
        if len(cleaned) >= 20:
            results.append(cleaned)
    return results[:5]


def build_experiments(
    plan,
    structured_experiments: list[dict] | None = None,
) -> list[ValidationExperiment]:
    if structured_experiments:
        return [
            ValidationExperiment(
                plan_id=plan.id,
                title=item["title"][:500],
                hypothesis=item.get("hypothesis"),
                method=item.get("method"),
                success_metric=item.get("success_metric"),
                budget=item.get("budget"),
                status="planned",
                priority=item.get("priority", "high"),
            )
            for item in structured_experiments
        ]
    recommendations = _recommendation_lines(plan.validation_strategy or "")
    if not recommendations:
        recommendations = [
            "Interview 10 target customers about the problem and their current alternatives.",
            "Test willingness to pay with a focused landing page and a measurable call to action.",
            "Build the smallest feasibility prototype and test the highest-risk technical assumption.",
        ]
    return [
        ValidationExperiment(
            plan_id=plan.id,
            title=item[:500],
            hypothesis=f"Evidence from this test will materially reduce uncertainty: {item}",
            method=item,
            success_metric="Define a numeric pass/fail threshold before starting.",
            status="planned",
            priority="high" if index == 0 else "medium",
        )
        for index, item in enumerate(recommendations)
    ]


def bootstrap_validation_workspace(
    plan,
    research_sources: list[dict] | None = None,
    financial_metrics: dict | None = None,
    structured_experiments: list[dict] | None = None,
) -> tuple[list, list, list]:
    """Return initial assumptions, evidence claims, and experiments for a plan."""
    return (
        build_assumptions(plan, financial_metrics),
        build_evidence_claims(plan, research_sources),
        build_experiments(plan, structured_experiments),
    )
