import { XMLParser } from "fast-xml-parser";

const [query, flag, value] = process.argv.slice(2);
if (!query || (flag && flag !== "--days") || (flag && !Number(value))) {
  console.error('usage: fetch.ts "<query>" [--days N]');
  process.exit(2);
}
const days = flag ? Number(value) : 1;
const url = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}+when:${days}d&hl=en-US&gl=US&ceid=US:en`;
const res = await fetch(url);
if (!res.ok) {
  console.error(`Google News: HTTP ${res.status}`);
  process.exit(1);
}
const rss = new XMLParser().parse(await res.text());
const items = [rss.rss.channel.item ?? []].flat().map((i: any) => ({
  title: i.title,
  url: i.link,
  source: typeof i.source === "string" ? i.source : i.source?.["#text"] ?? "Google News",
  published_at: new Date(i.pubDate).toISOString(),
}));
items.sort((a, b) => b.published_at.localeCompare(a.published_at));
const seen = new Set<string>();
for (const item of items) {
  if (seen.has(item.url)) continue;
  seen.add(item.url);
  console.log(JSON.stringify(item));
}
