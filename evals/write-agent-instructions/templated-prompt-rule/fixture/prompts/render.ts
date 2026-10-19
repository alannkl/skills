// Fills {{company_name}}, {{customer_name}} and other double-brace placeholders per conversation.
export function render(template: string, values: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key: string) => values[key] ?? '');
}
