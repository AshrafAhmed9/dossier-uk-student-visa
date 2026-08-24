"""Deterministically assesses the narrow UK Student financial requirement.

This module intentionally has no network or agent imports. Gemini can help
collect facts, but only this code turns cited facts into a requirement status.
It is evidence assembly, not legal advice.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from rulebook.graph import RequirementGraph


class Status(StrEnum):
    SATISFIED = "satisfied"
    UNSATISFIED = "unsatisfied"
    BLOCKED = "blocked_until"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class CaseFacts:
    study_in_london: bool | None = None
    course_months: int | None = None
    outstanding_course_fees_gbp: int | None = None
    bank_balance_gbp: int | None = None
    funds_held_since: date | None = None
    evidence_closing_date: date | None = None
    months_in_uk_with_permission: int | None = None
    applying_permission_to_stay: bool = False


@dataclass(frozen=True)
class NodeAssessment:
    node_id: str
    status: Status
    citation: str
    source_url: str
    explanation: str
    blocked_until: date | None = None


@dataclass(frozen=True)
class Assessment:
    required_funds_gbp: int | None
    nodes: tuple[NodeAssessment, ...]
    earliest_apply_date: date | None
    latest_apply_date: date | None

    @property
    def eligible_now(self) -> bool:
        return all(node.status in {Status.SATISFIED, Status.NOT_APPLICABLE} for node in self.nodes)


LONDON_MONTHLY = 1529
OUTSIDE_LONDON_MONTHLY = 1171
HOLDING_DAYS = 28
EVIDENCE_RECENCY_DAYS = 31


def _node(graph: RequirementGraph, node_id: str):
    return graph.by_id(node_id)


def _assessment(graph: RequirementGraph, node_id: str, status: Status, explanation: str,
                blocked_until: date | None = None) -> NodeAssessment:
    node = _node(graph, node_id)
    return NodeAssessment(node_id, status, node.citation, node.source_url, explanation, blocked_until)


def required_funds(facts: CaseFacts) -> int | None:
    if None in (facts.study_in_london, facts.course_months, facts.outstanding_course_fees_gbp):
        return None
    monthly = LONDON_MONTHLY if facts.study_in_london else OUTSIDE_LONDON_MONTHLY
    return facts.outstanding_course_fees_gbp + monthly * min(facts.course_months, 9)


def assess(graph: RequirementGraph, facts: CaseFacts, as_of: date | None = None) -> Assessment:
    """Evaluates the cited graph using supplied facts only; no model judgment."""
    as_of = as_of or date.today()
    exempt = facts.applying_permission_to_stay and (facts.months_in_uk_with_permission or 0) >= 12
    if exempt:
        node_ids = ("st_12_1_exemption", "st_12_3_london", "st_12_3_outside_london", "st_12_6_holding_period", "fin_7_1_recency", "fin_7_2_count_back")
        return Assessment(None, tuple(
            _assessment(graph, node_id, Status.SATISFIED if node_id == "st_12_1_exemption" else Status.NOT_APPLICABLE,
                        "12+ months of UK permission for a permission-to-stay application; financial evidence is not required." if node_id == "st_12_1_exemption" else "Pruned because ST 12.1 is met.")
            for node_id in node_ids
        ), as_of, None)

    total = required_funds(facts)
    location_node = "st_12_3_london" if facts.study_in_london else "st_12_3_outside_london"
    nodes = [_assessment(graph, "st_12_1_exemption", Status.NOT_APPLICABLE,
                         "This case is being assessed under the standard financial requirement; the ST 12.1 exemption does not apply.")]
    if total is None:
        nodes.append(_assessment(graph, location_node, Status.UNKNOWN, "Need study location, course duration, and outstanding course fees."))
    elif facts.bank_balance_gbp is None:
        nodes.append(_assessment(graph, location_node, Status.UNKNOWN, f"Need current balance. Required funds calculate to £{total:,}."))
    elif facts.bank_balance_gbp >= total:
        nodes.append(_assessment(graph, location_node, Status.SATISFIED, f"Balance £{facts.bank_balance_gbp:,} meets calculated requirement £{total:,}."))
    else:
        nodes.append(_assessment(graph, location_node, Status.UNSATISFIED, f"Balance £{facts.bank_balance_gbp:,} is £{total - facts.bank_balance_gbp:,} below calculated requirement £{total:,}."))

    earliest = None
    latest = facts.evidence_closing_date + timedelta(days=EVIDENCE_RECENCY_DAYS) if facts.evidence_closing_date else None
    if not facts.funds_held_since or not facts.evidence_closing_date:
        nodes.append(_assessment(graph, "st_12_6_holding_period", Status.UNKNOWN, "Need funds-held start date and evidence closing date."))
        nodes.append(_assessment(graph, "fin_7_1_recency", Status.UNKNOWN, "Need most recent evidence closing date."))
        nodes.append(_assessment(graph, "fin_7_2_count_back", Status.UNKNOWN, "Need closing date to count back the holding period."))
    else:
        earliest = facts.funds_held_since + timedelta(days=HOLDING_DAYS - 1)
        held_days = (facts.evidence_closing_date - facts.funds_held_since).days + 1
        holding_status = Status.SATISFIED if held_days >= HOLDING_DAYS else Status.BLOCKED
        nodes.append(_assessment(graph, "st_12_6_holding_period", holding_status,
                                 f"Funds have been held for {held_days} consecutive day(s).", earliest if holding_status == Status.BLOCKED else None))
        recency_age = (as_of - facts.evidence_closing_date).days
        recency_status = Status.SATISFIED if 0 <= recency_age <= EVIDENCE_RECENCY_DAYS else Status.UNSATISFIED
        nodes.append(_assessment(graph, "fin_7_1_recency", recency_status,
                                 f"Evidence is {recency_age} day(s) old on the assessment date."))
        nodes.append(_assessment(graph, "fin_7_2_count_back", Status.SATISFIED,
                                 "Holding-period arithmetic counts back from the supplied closing balance date."))

    if total is None or facts.bank_balance_gbp is None or facts.bank_balance_gbp < total:
        earliest = None
    elif earliest is not None and latest is not None and earliest > latest:
        # A statement can be too old by the time the 28-day period completes, so
        # presenting separate dates as an "apply window" would be misleading.
        earliest = None
        latest = None
    return Assessment(total, tuple(nodes), earliest, latest)
