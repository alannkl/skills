// Fails if code calls t("key") for a key missing from locales/en/<namespace>.json.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

function flatten(obj, prefix = "") {
  return Object.entries(obj).flatMap(([k, v]) =>
    typeof v === "object" ? flatten(v, `${prefix}${k}.`) : [`${prefix}${k}`],
  );
}

function walk(dir) {
  return readdirSync(dir).flatMap((f) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : p.endsWith(".tsx") ? [p] : [];
  });
}

const missing = [];
for (const file of walk("src")) {
  const src = readFileSync(file, "utf8");
  const ns = src.match(/useTranslation\("([^"]+)"\)/)?.[1];
  if (!ns) continue;
  const keys = new Set(flatten(JSON.parse(readFileSync(`locales/en/${ns}.json`, "utf8"))));
  for (const [, key] of src.matchAll(/\bt\("([^"]+)"/g)) {
    if (!keys.has(key) && !keys.has(`${key}_one`)) missing.push(`${file}: ${ns}:${key}`);
  }
}

if (missing.length) {
  console.error("Missing keys in en:\n" + missing.join("\n"));
  process.exit(1);
}
console.log("i18n ok");
