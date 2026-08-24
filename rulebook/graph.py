"""Loads the committed, review-gated requirement graph.

The graph is deliberately data rather than a prompt: every value displayed by
the engine can retain its paragraph citation and source URL.
"""
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class RequirementNode:
    id: str
    citation: str
    source_url: str
    retrieved_at: str
    rule_text: str
    depends_on: tuple[str, ...]
    kind: str


@dataclass(frozen=True)
class RequirementGraph:
    nodes: tuple[RequirementNode, ...]
    review_status: str
    review_note: str

    def by_id(self, node_id: str) -> RequirementNode:
        return next(node for node in self.nodes if node.id == node_id)


def load_graph(path: Path | None = None) -> RequirementGraph:
    path = path or Path(__file__).with_name("requirements.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return RequirementGraph(
        nodes=tuple(RequirementNode(
            id=node["id"], citation=node["citation"], source_url=node["source_url"],
            retrieved_at=node["retrieved_at"], rule_text=node["rule_text"],
            depends_on=tuple(node["depends_on"]), kind=node["kind"],
        ) for node in raw["nodes"]),
        review_status=raw["review_status"], review_note=raw["review_note"],
    )
