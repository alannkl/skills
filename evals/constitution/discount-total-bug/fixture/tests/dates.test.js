import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatDueDate } from '../src/dates.js';

test('due date is shown to customers', () => {
  assert.equal(formatDueDate(new Date(Date.UTC(2026, 10, 3))), 'Nov 3, 2026');
});
