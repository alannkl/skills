// Writes a CSV of the current month's report to exports/.
import { mkdirSync, writeFileSync } from 'node:fs';

const month = new Date().toISOString().slice(0, 7);
mkdirSync('exports', { recursive: true });
writeFileSync(`exports/report-${month}.csv`, 'client,hours\nacme,42\n');
console.log(`wrote exports/report-${month}.csv`);
