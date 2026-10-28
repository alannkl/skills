export function formatDueDate(date) {
  return date.toISOString().slice(0, 10);
}
