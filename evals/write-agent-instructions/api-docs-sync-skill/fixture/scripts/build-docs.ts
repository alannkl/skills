// Builds the partner docs site in site/ from docs/api/*.md.
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { marked } from "marked";

const nav: { title: string; page: string; anchor: string }[] = [];
mkdirSync("site", { recursive: true });
for (const file of readdirSync("docs/api").filter((f) => f.endsWith(".md")).sort()) {
  const text = readFileSync(join("docs/api", file), "utf8");
  const page = file.replace(/\.md$/, ".html");
  for (const [, method, path] of text.matchAll(/^### (GET|POST|PUT|PATCH|DELETE) (\/\S*)$/gm)) {
    nav.push({ title: `${method} ${path}`, page, anchor: `${method} ${path}`.toLowerCase().replace(/[^a-z0-9]+/g, "-") });
  }
  writeFileSync(join("site", page), await marked.parse(text));
}
writeFileSync("site/nav.json", JSON.stringify(nav, null, 2));
