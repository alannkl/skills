#!/usr/bin/env node
// acme: command-line client for the Acme API.
const { version } = require("../package.json");
const login = require("../lib/login");
const session = require("../lib/session");

const [command, ...args] = process.argv.slice(2);
const commands = {
  login: () => login(),
  logout: () => session.clear(),
  whoami: () => console.log(session.load()?.user ?? "not signed in"),
  export: () => console.log(`exporting orders as ${args[args.indexOf("--format") + 1] || "json"}`),
};

if (command === "--version") console.log(version);
else if (commands[command]) commands[command]();
else {
  console.error(`usage: acme <${Object.keys(commands).join("|")}|--version>`);
  process.exit(2);
}
