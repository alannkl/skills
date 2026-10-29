const [query, flag, value] = process.argv.slice(2);
if (!query || (flag && flag !== "--days") || (flag && !Number(value))) {
  console.error('usage: fetch.ts "<query>" [--days N]');
  process.exit(2);
}
const days = flag ? Number(value) : 1;
const url = `https://api.gdeltproject.org/api/v2/doc/doc?query=${encodeURIComponent(query)}&mode=artlist&format=json&sort=datedesc&maxrecords=75&timespan=${days}d`;
const res = await fetch(url);
if (!res.ok) {
  console.error(`GDELT: HTTP ${res.status}`);
  process.exit(1);
}
const { articles = [] } = (await res.json()) as { articles?: any[] };
// seendate looks like 20261029T101500Z
const iso = (d: string) =>
  `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}T${d.slice(9, 11)}:${d.slice(11, 13)}:${d.slice(13, 15)}Z`;
const items = articles.map((a) => ({
  title: a.title,
  url: a.url,
  source: a.domain,
  publishedAt: iso(a.seendate),
}));
items.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt));
const seen = new Set<string>();
for (const item of items) {
  if (seen.has(item.url)) continue;
  seen.add(item.url);
  console.log(JSON.stringify(item));
}
