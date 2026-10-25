import os

import psycopg
import pytest

URL = os.environ.get("WAREHOUSE_URL", "postgresql://ledger:ledger@localhost:5433/ledger")


@pytest.fixture
def conn():
    with psycopg.connect(URL) as c:
        with c.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS transactions ("
                "transaction_id text primary key, amount numeric, currency text, booked_at timestamptz)"
            )
            cur.execute("TRUNCATE transactions")
        c.commit()
        yield c
