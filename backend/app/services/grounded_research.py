"""Provider-independent web research with source-aware LLM synthesis."""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

from ddgs import DDGS

from app.services.llm import ask_llm

logger = logging.getLogger(__name__)
LOW_SIGNAL_DOMAINS = {
    "instagram.com",
    "linkedin.com",
    "pinterest.com",
    "facebook.com",
    "tiktok.com",
}


def _compact_idea(idea: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", idea).strip()
    return value[:limit]


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _source_quality(url: str) -> tuple[int, str]:
    domain = _domain(url)
    if domain.endswith(".gov") or domain.endswith(".gov.et"):
        return 90, "government"
    if any(name in domain for name in ("worldbank.org", "oecd.org", "un.org", "europa.eu")):
        return 90, "institutional"
    if domain.endswith(".edu"):
        return 85, "academic"
    if any(name in domain for name in ("reuters.com", "sec.gov", "crunchbase.com")):
        return 75, "business-data"
    if any(name in domain for name in (
        "grandviewresearch.com",
        "mordorintelligence.com",
        "gartner.com",
        "idc.com",
        "statista.com",
        "marketsandmarkets.com",
    )):
        return 65, "market-research"
    return 45, "web"


def collect_market_sources(idea: str, max_per_query: int = 5) -> list[dict]:
    """Search several market angles and return deduplicated source metadata."""
    subject = _compact_idea(idea)
    queries = [
        f"{subject} market size growth statistics",
        f"{subject} competitors pricing funding",
        f"{subject} industry regulation trends",
    ]
    sources: list[dict] = []
    seen_urls: set[str] = set()
    try:
        search = DDGS()
        for query in queries:
            for result in search.text(query, max_results=max_per_query):
                url = (result.get("href") or result.get("url") or "").strip()
                title = (result.get("title") or _domain(url) or "Untitled source").strip()
                snippet = re.sub(r"\s+", " ", (result.get("body") or "").strip())
                if not url.startswith(("http://", "https://")) or url in seen_urls:
                    continue
                domain = _domain(url)
                if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in LOW_SIGNAL_DOMAINS):
                    continue
                seen_urls.add(url)
                confidence, source_type = _source_quality(url)
                sources.append(
                    {
                        "id": f"S{len(sources) + 1}",
                        "title": title[:180],
                        "url": url,
                        "snippet": snippet[:900],
                        "query": query,
                        "domain": domain,
                        "confidence": confidence,
                        "source_type": source_type,
                    }
                )
    except Exception as exc:
        logger.warning("Market source retrieval failed error_type=%s", type(exc).__name__)
    ranked = sorted(sources, key=lambda item: item["confidence"], reverse=True)
    selected: list[dict] = []
    domain_counts: dict[str, int] = {}
    for source in ranked:
        domain = source["domain"]
        if domain_counts.get(domain, 0) >= 2:
            continue
        selected.append(source)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        if len(selected) == 12:
            break
    # Citation IDs must match the final packet order.
    for index, source in enumerate(selected, 1):
        source["id"] = f"S{index}"
    return selected


def _research_packet(sources: list[dict]) -> str:
    return "\n\n".join(
        (
            f"[{source['id']}] {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Source type: {source['source_type']}\n"
            f"Search excerpt: {source['snippet'] or 'No excerpt available.'}"
        )
        for source in sources
    )


def grounded_market_analysis(idea: str, extra_info: str = "") -> tuple[str, list[dict]]:
    """Retrieve sources and synthesize a market report with inline citations."""
    sources = collect_market_sources(idea)
    if not sources:
        return "", []

    prompt = f"""You are a rigorous startup market-research analyst.

Startup idea:
{idea}

Founder context:
{extra_info or "None provided"}

You must base factual market claims on the research packet below.

RESEARCH PACKET
{_research_packet(sources)}

Rules:
1. Cite every factual claim using individual Markdown links in this exact form:
   [S1](source URL) [S2](source URL). Never combine IDs as [S1, S2].
2. Never invent a source, URL, funding number, market size, growth rate, or regulation.
3. Search excerpts are leads, not proof. If evidence is incomplete, say "Evidence gap".
4. Clearly label calculated TAM/SAM/SOM values as founder assumptions unless a source supports them.
5. Distinguish the broad adjacent market from the startup's actual serviceable market.
6. Do not claim that a source has been independently verified.
7. Prefer higher-authority institutional, government, academic, and primary sources.
8. Put one decision-relevant claim per bullet so every claim can be mapped to its source.
9. Do not turn section labels such as "Supported claims" into bullet items.

Return this structure:

## Research Confidence
- Source coverage summary
- Important evidence gaps

## Market Overview
- Supported market size and growth claims
- TAM/SAM/SOM, with assumptions explicitly labeled
- Key market drivers

## Target Customers
- Primary segments
- Customer pain points
- Buying behavior and evidence gaps

## Competitive Landscape
- Named competitors found in the packet
- Positioning and pricing only when supported
- Market gaps

## Industry Trends
- Technology trends
- Regulatory considerations
- Emerging opportunities

## Source Index
- One bullet per cited source: [S# — title](URL) — why it matters
"""
    return ask_llm(prompt), sources
