import { expect, test } from 'vitest';
import { render } from './render';
import { supportSystemPrompt } from './support';

test('rendering fills every placeholder', () => {
  const text = render(supportSystemPrompt(['refund', 'lookup_order']), { company_name: 'Acme', customer_name: 'Sam' });
  expect(text).not.toContain('{{');
  expect(text).toContain('[[ESCALATE]]');
});
