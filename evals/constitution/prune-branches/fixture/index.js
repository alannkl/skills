module.exports = { total: (lines) => lines.reduce((s, l) => s + l.cents, 0) };
