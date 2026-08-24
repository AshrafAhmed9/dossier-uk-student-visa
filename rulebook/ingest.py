"""Fetch the two official sources for a human rulebook review.

This intentionally does not rewrite ``requirements.json``. A person must review
the cited source text before changing the committed decision artifact.
"""
from __future__ import annotations

from urllib.request import Request, urlopen

from rulebook.graph import load_graph


USER_AGENT = "Dossier-rulebook-review/1.0 (human-reviewed evidence assembly)"


def fetch_source(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:  # nosec B310: fixed official GOV.UK URLs from the graph
        return response.read().decode("utf-8", errors="replace")


def audit_sources() -> list[dict[str, str | bool]]:
    """Return review evidence without pretending that automated matching is approval."""
    graph = load_graph()
    pages: dict[str, str] = {}
    results = []
    for node in graph.nodes:
        page = pages.setdefault(node.source_url, fetch_source(node.source_url))
        results.append({
            "citation": node.citation,
            "source_url": node.source_url,
            "rule_text_found": node.rule_text in page,
            "review_status": graph.review_status,
        })
    return results


if __name__ == "__main__":
    for result in audit_sources():
        print(result)
