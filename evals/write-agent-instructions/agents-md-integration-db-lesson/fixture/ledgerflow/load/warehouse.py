import os

import pandas as pd
import psycopg


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["WAREHOUSE_URL"])


def upsert_transactions(conn: psycopg.Connection, df: pd.DataFrame) -> int:
    rows = df[["transaction_id", "amount", "currency", "booked_at"]].itertuples(index=False)
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO transactions (transaction_id, amount, currency, booked_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE
              SET amount = EXCLUDED.amount, currency = EXCLUDED.currency, booked_at = EXCLUDED.booked_at
            """,
            list(rows),
        )
    conn.commit()
    return len(df)
