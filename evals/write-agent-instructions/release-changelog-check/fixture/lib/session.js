// Session token storage and refresh.
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const file = path.join(os.homedir(), ".acme", "session.json");

function load() {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : null;
}

function clear() { fs.rmSync(file, { force: true }); }

function needsRefresh(session) {
  return Date.now() >= session.expiresAt;
}

module.exports = { load, clear, needsRefresh };
