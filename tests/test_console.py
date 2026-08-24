from console import main


def test_question_preference_is_persisted_separately_from_case_facts(tmp_path, monkeypatch):
    preference_path = tmp_path / "preferences.json"
    monkeypatch.setattr(main, "PREFERENCE_PATH", preference_path)
    main.save_preference("brief and checklist-like")
    assert main._question_style() == "brief and checklist-like"


def test_form_helpers_reject_negative_money_and_invalid_dates():
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        main._integer_or_none("-1", "Balance")
    with pytest.raises(HTTPException):
        main._date_or_none("not-a-date", "Date")
