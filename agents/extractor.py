"""Evidence extraction is confirmation-first; nothing extracted becomes a fact silently."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ExtractedEvidence:
    account_holder: str | None = None
    institution: str | None = None
    closing_balance_gbp: int | None = None
    closing_date: date | None = None
    needs_confirmation: bool = True


def extraction_prompt() -> str:
    return ("Extract account holder, financial institution, closing balance in GBP, and statement closing date. "
            "Return null where unclear. This is a candidate extraction only and must be confirmed by the user.")
