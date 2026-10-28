import 'dotenv/config';
import pg from 'pg';
import { readdirSync, readFileSync } from 'node:fs';

export async function migrate() {
  const client = new pg.Client({ connectionString: process.env.DATABASE_URL });
  await client.connect();
  await client.query('CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY)');
  const done = new Set((await client.query('SELECT name FROM schema_migrations')).rows.map((r) => r.name));
  for (const name of readdirSync('migrations').sort()) {
    if (done.has(name)) continue;
    await client.query(readFileSync(`migrations/${name}`, 'utf8'));
    await client.query('INSERT INTO schema_migrations (name) VALUES ($1)', [name]);
    console.log(`applied ${name}`);
  }
  await client.end();
}

if (import.meta.url === `file://${process.argv[1]}`) await migrate();
