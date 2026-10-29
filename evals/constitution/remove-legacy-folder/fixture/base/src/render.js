function render(template, data) {
  return template.replace(/\{\{(\w+)\}\}/g, (_, key) => String(data[key] ?? ''));
}
module.exports = { render };
