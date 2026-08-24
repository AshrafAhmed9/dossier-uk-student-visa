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
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        main._integer_or_none("-1", "Balance")
    with pytest.raises(HTTPException):
        main._date_or_none("not-a-date", "Date")
