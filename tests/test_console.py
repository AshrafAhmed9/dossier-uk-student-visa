import asyncio
from datetime import date
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from agents.extractor import ExtractedEvidence
from console import main


class MemoryStore:
    def __init__(self):
        self.values = {}

    def load(self, name):
        return self.values.get(name, {})

    def save(self, name, value):
        self.values[name] = value


def test_question_preference_is_persisted_separately_from_case_facts(tmp_path, monkeypatch):
    memory = MemoryStore()
    monkeypatch.setattr(main, "store", memory)
    main.save_preference("brief and checklist-like")
    assert main._question_style() == "brief and checklist-like"
    assert memory.load("case") == {}


def test_form_helpers_reject_negative_money_and_invalid_dates():
    with pytest.raises(HTTPException):
        main._integer_or_none("-1", "Balance")
    with pytest.raises(HTTPException):
        main._date_or_none("not-a-date", "Date")


def test_uploaded_evidence_stays_pending_until_the_user_confirms(monkeypatch):
    memory = MemoryStore()
    monkeypatch.setattr(main, "store", memory)
    monkeypatch.setattr(main, "extract", lambda image, mime: ExtractedEvidence(
        account_holder="A. Student", institution="Example Bank", closing_balance_gbp=15539,
        closing_date=date(2026, 8, 28),
    ))

    response = asyncio.run(main.upload_evidence(UploadFile(
        file=BytesIO(b"image-bytes"), filename="statement.png", headers={"content-type": "image/png"},
    )))

    assert response.status_code == 200
    assert memory.load("case") == {}
    assert memory.load("pending_evidence")["needs_confirmation"] is True

    confirmation = main.confirm_evidence("A. Student", "Example Bank", "15539", "2026-08-28")
    assert confirmation.status_code == 303
    assert memory.load("case") == {"bank_balance_gbp": 15539, "evidence_closing_date": "2026-08-28"}
    assert memory.load("confirmed_evidence")["confirmed_by_user"] is True
    assert memory.load("pending_evidence") == {}


def test_confirmation_requires_a_pending_extraction(monkeypatch):
    monkeypatch.setattr(main, "store", MemoryStore())
    with pytest.raises(HTTPException, match="no extracted evidence"):
        main.confirm_evidence("", "", "", "")
