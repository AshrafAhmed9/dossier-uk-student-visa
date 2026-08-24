from datetime import date, timedelta
import ast
from pathlib import Path

from engine.gaps import CaseFacts, Status, assess, required_funds
from rulebook.graph import load_graph


GRAPH = load_graph()
TODAY = date(2026, 8, 24)


def facts(**overrides):
    base = dict(study_in_london=False, course_months=9, outstanding_course_fees_gbp=5_000,
                bank_balance_gbp=15_539, funds_held_since=TODAY - timedelta(days=27),
                evidence_closing_date=TODAY, months_in_uk_with_permission=0)
    base.update(overrides)
    return CaseFacts(**base)


def node(result, node_id):
    return next(n for n in result.nodes if n.node_id == node_id)


def test_current_amounts_and_london_split():
    assert required_funds(facts()) == 15_539
    assert required_funds(facts(study_in_london=True)) == 18_761


def test_holding_period_boundaries_are_inclusive():
    assert node(assess(GRAPH, facts(funds_held_since=TODAY - timedelta(days=26)), TODAY), "st_12_6_holding_period").status == Status.BLOCKED
    assert node(assess(GRAPH, facts(funds_held_since=TODAY - timedelta(days=27)), TODAY), "st_12_6_holding_period").status == Status.SATISFIED
    assert node(assess(GRAPH, facts(funds_held_since=TODAY - timedelta(days=28)), TODAY), "st_12_6_holding_period").status == Status.SATISFIED


def test_evidence_recency_boundaries():
    assert node(assess(GRAPH, facts(evidence_closing_date=TODAY - timedelta(days=30)), TODAY), "fin_7_1_recency").status == Status.SATISFIED
    assert node(assess(GRAPH, facts(evidence_closing_date=TODAY - timedelta(days=31)), TODAY), "fin_7_1_recency").status == Status.SATISFIED
    assert node(assess(GRAPH, facts(evidence_closing_date=TODAY - timedelta(days=32)), TODAY), "fin_7_1_recency").status == Status.UNSATISFIED


def test_12_month_permission_exemption_prunes_fund_nodes():
    result = assess(GRAPH, facts(months_in_uk_with_permission=12, applying_permission_to_stay=True, bank_balance_gbp=0), TODAY)
    assert result.eligible_now
    assert node(result, "st_12_3_outside_london").status == Status.NOT_APPLICABLE


def test_insufficient_balance_is_never_model_judgment():
    result = assess(GRAPH, facts(bank_balance_gbp=10_000), TODAY)
    assert node(result, "st_12_3_outside_london").status == Status.UNSATISFIED
    assert "£5,539" in node(result, "st_12_3_outside_london").explanation


def test_engine_never_imports_agents():
    tree = ast.parse(Path("engine/gaps.py").read_text())
    imported = [alias.name for stmt in ast.walk(tree) if isinstance(stmt, (ast.Import, ast.ImportFrom)) for alias in stmt.names]
    assert not any(name.startswith("agents") for name in imported)
