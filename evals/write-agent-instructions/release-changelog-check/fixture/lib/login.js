// Browser sign-in for `acme login`.
const { spawn } = require("node:child_process");

module.exports = function login() {
  const opener = process.platform === "darwin" ? "open" : "xdg-open";
  const browser = spawn(opener, ["https://acme.example.com/cli-login"], { stdio: "ignore" });
  browser.on("exit", () => process.exit(0));
};
