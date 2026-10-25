import pandas as pd

from ledgerflow.load.warehouse import upsert_transactions


def test_upsert_is_idempotent(conn):
    df = pd.DataFrame(
        {
            "transaction_id": ["t1", "t2"],
            "amount": [1.0, 2.0],
            "currency": ["EUR", "EUR"],
            "booked_at": pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
        }
    )
    upsert_transactions(conn, df)
    upsert_transactions(conn, df)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM transactions")
        assert cur.fetchone()[0] == 2
