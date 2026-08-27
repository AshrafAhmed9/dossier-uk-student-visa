from datetime import date

import pytest

from agents.extractor import _json_object, _optional_balance, _optional_date


def test_extraction_parser_accepts_the_expected_json_shape():
    payload = _json_object('```json\n{"account_holder":"A. Student","closing_balance_gbp":15539,"closing_date":"2026-08-28"}\n```')
    assert payload["account_holder"] == "A. Student"
    assert _optional_balance(payload["closing_balance_gbp"]) == 15539
    assert _optional_date(payload["closing_date"]) == date(2026, 8, 28)


@pytest.mark.parametrize("value", [True, -1, "not-a-number"])
def test_extraction_parser_rejects_invalid_balances(value):
    with pytest.raises(ValueError, match="invalid balance"):
        _optional_balance(value)


def test_extraction_parser_rejects_invalid_dates():
    with pytest.raises(ValueError, match="invalid date"):
        _optional_date("28/08/2026")
