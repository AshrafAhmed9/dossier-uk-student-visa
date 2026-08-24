from rulebook.graph import load_graph


def test_every_rule_node_is_sourceable_and_review_gated():
    graph = load_graph()
    assert graph.review_status == "REQUIRES_HUMAN_REVIEW"
    for node in graph.nodes:
        assert node.citation
        assert node.source_url.startswith("https://www.gov.uk/")
        assert node.retrieved_at
        assert node.rule_text
