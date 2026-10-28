import { readFileSync } from 'node:fs';

export const config = JSON.parse(readFileSync(new URL('../config/default.json', import.meta.url)));
