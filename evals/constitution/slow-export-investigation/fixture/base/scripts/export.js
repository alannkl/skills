// Nightly export of every order to the warehouse bucket, run by cron at 02:00.
const { Pool } = require('pg');
const QueryStream = require('pg-query-stream');
const { createWriteStream } = require('fs');

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function main() {
  const client = await pool.connect();
  const out = createWriteStream(process.argv[2] || '/tmp/orders.csv');
  const started = Date.now();
  let rows = 0;
  const stream = client.query(new QueryStream(
    'SELECT o.id, o.customer_id, o.total_cents, o.created_at FROM orders o ORDER BY o.id'));
  for await (const row of stream) {
    out.write([row.id, row.customer_id, row.total_cents, row.created_at.toISOString()].join(',') + '\n');
    rows += 1;
  }
  out.end();
  client.release();
  console.log(`rows exported ${rows}, duration ${Math.round((Date.now() - started) / 60000)}m`);
  await pool.end();
}

main().catch((err) => { console.error(err); process.exit(1); });
