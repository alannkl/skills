import pandas as pd


def normalize_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """Convert minor-unit integer amounts to decimal major units."""
    df["amount"] = df["amount_minor"] / 100
    df = df.drop(columns=["amount_minor"])
    return df


def dedupe(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["transaction_id"], keep="last")
