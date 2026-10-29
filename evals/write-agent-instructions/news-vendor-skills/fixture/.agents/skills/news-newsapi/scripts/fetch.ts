const [query, flag, value] = process.argv.slice(2);
if (!query || (flag && flag !== "--days") || (flag && !Number(value))) {
  console.error('usage: fetch.ts "<query>" [--days N]');
  process.exit(2);
}
const key = process.env.NEWSAPI_KEY;
if (!key) {
  console.error("NEWSAPI_KEY is not set");
  process.exit(2);
}
const days = flag ? Number(value) : 1;
const from = new Date(Date.now() - days * 86_400_000).toISOString();
const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(query)}&from=${from}&sortBy=publishedAt&language=en&pageSize=50`;
const res = await fetch(url, { headers: { "X-Api-Key": key } });
if (!res.ok) {
  console.error(`NewsAPI: HTTP ${res.status}`);
  process.exit(1);
}
const { articles } = (await res.json()) as { articles: any[] };
const items = articles.map((a) => ({
  title: a.title,
  url: a.url,
  source: a.source?.name ?? "NewsAPI",
  published_at: new Date(a.publishedAt).toISOString(),
}));
items.sort((a, b) => b.published_at.localeCompare(a.published_at));
const seen = new Set<string>();
for (const item of items) {
  if (seen.has(item.title)) continue;
  seen.add(item.title);
  console.log(JSON.stringify(item));
}
