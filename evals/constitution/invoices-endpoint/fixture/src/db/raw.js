// Deprecated for new code: put queries in a repository under src/repos/ (docs/adr/007-repositories.md).
// Existing callers move over when they are next reworked.
import pg from 'pg';

export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

export async function query(sql, params) {
  const { rows } = await pool.query(sql, params);
  return rows;
}
