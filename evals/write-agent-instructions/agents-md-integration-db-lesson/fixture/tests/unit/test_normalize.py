import pandas as pd

from ledgerflow.transform.normalize import dedupe, normalize_amounts


def test_normalize_amounts():
    df = pd.DataFrame({"amount_minor": [1050, 99]})
    out = normalize_amounts(df)
    assert list(out["amount"]) == [10.5, 0.99]


def test_dedupe_keeps_last():
    df = pd.DataFrame({"transaction_id": ["a", "a"], "amount": [1, 2]})
    assert list(dedupe(df)["amount"]) == [2]
