// Parses CHANGELOG.md. With --check, exits 1 on any line outside the format below. Without it, copies the newest
// released version's entries verbatim into app/whats-new.json for the What's New panel.
import { readFileSync, writeFileSync } from "node:fs";

const SECTIONS = ["Added", "Changed", "Fixed"];
const versions: { version: string; entries: { section: string; text: string }[] }[] = [];
const errors: string[] = [];
let section = -1;

readFileSync("CHANGELOG.md", "utf8").split("\n").forEach((line, i) => {
  let m: RegExpMatchArray | null;
  if (line === "" || (i === 0 && line === "# Changelog")) return;
  if ((m = line.match(/^## \[(Unreleased)\]$|^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$/))) {
    versions.push({ version: m[1] ?? m[2], entries: [] });
    section = -1;
  } else if ((m = line.match(/^### (\w+)$/)) && versions.length && SECTIONS.indexOf(m[1]) > section) {
    section = SECTIONS.indexOf(m[1]);
  } else if (line.startsWith("- ") && section >= 0) {
    versions.at(-1)!.entries.push({ section: SECTIONS[section], text: line.slice(2) });
  } else {
    errors.push(`CHANGELOG.md:${i + 1}: unexpected line: ${line}`);
  }
});

if (process.argv.includes("--check")) {
  errors.forEach((e) => console.error(e));
  process.exit(errors.length ? 1 : 0);
}
const latest = versions.find((v) => v.version !== "Unreleased");
writeFileSync("app/whats-new.json", JSON.stringify(latest, null, 2) + "\n");
