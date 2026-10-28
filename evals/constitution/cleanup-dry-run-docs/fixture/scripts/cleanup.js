// Deletes exported reports older than --days (default 30) from exports/.
import { readdirSync, statSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';

const { values } = parseArgs({ options: { days: { type: 'string', default: '30' } } });
const days = Number(values.days);
if (!Number.isFinite(days) || days < 0) {
  console.error(`--days must be a non-negative number, got ${values.days}`);
  process.exit(1);
}

const dir = 'exports';
const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
let removed = 0;
for (const name of readdirSync(dir)) {
  const path = join(dir, name);
  const stats = statSync(path);
  if (stats.isFile() && stats.mtimeMs < cutoff) {
    rmSync(path);
    removed++;
  }
}
console.log(`removed ${removed} file(s) older than ${days} day(s)`);
