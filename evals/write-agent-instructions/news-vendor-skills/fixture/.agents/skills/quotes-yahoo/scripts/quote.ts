const tickers = process.argv.slice(2);
if (tickers.length === 0) {
  console.error("usage: quote.ts <TICKER>...");
  process.exit(2);
}
for (const ticker of tickers) {
  const res = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=5d&interval=1d`);
  if (res.status === 404) {
    console.log(JSON.stringify({ ticker, error: "unknown ticker" }));
    continue;
  }
  if (!res.ok) {
    console.error(`Yahoo Finance: HTTP ${res.status}`);
    process.exit(1);
  }
  const meta = (await res.json()).chart.result[0].meta;
  const close = meta.regularMarketPrice;
  const prev = meta.chartPreviousClose;
  console.log(JSON.stringify({
    ticker,
    close,
    change: +(close - prev).toFixed(2),
    change_pct: +(((close - prev) / prev) * 100).toFixed(2),
    currency: meta.currency,
  }));
}
