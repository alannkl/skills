import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

export async function postEntry({ account, amountCents, memo }) {
  const { rows } = await pool.query(
    "insert into entries (account, amount_cents, memo) values ($1, $2, $3) returning *",
    [account, amountCents, memo ?? null],
  );
  return rows[0];
}

export async function listEntries(account) {
  const { rows } = await pool.query(
    "select * from entries where account = $1 order by created_at desc",
    [account],
  );
  return rows;
}
