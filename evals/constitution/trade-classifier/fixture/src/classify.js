// Classifies a wallet's swap transaction as a buy or sell of a token against a quote asset.
const QUOTES = new Set(['ETH', 'WETH', 'USDC', 'USDT']);

const ROUTERS = {
  '0x7a250d5630b4cf539739df2c5dacb4c659f2488d': 'uniswap-v2',
  '0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f': 'sushiswap',
  '0x1111111254eeb25477b68fb85ed929f73a960582': '1inch',
};

export function classify(tx) {
  const router = ROUTERS[tx.to.toLowerCase()];
  if (router === 'uniswap-v2' || router === 'sushiswap') return classifyV2(tx);
  if (router === '1inch') return classifyOneInch(tx);
  return { side: 'unknown' };
}

function classifyV2(tx) {
  const sent = tx.transfers.find((t) => t.from === tx.wallet);
  const received = tx.transfers.find((t) => t.to === tx.wallet);
  if (tx.method === 'swapExactETHForTokens') return { side: 'buy', token: received.token, quote: 'ETH' };
  if (tx.method.startsWith('swapExactTokensForETH')) return { side: 'sell', token: sent.token, quote: 'ETH' };
  if (tx.method === 'swapExactTokensForTokens') {
    if (QUOTES.has(sent.token)) return { side: 'buy', token: received.token, quote: sent.token };
    if (QUOTES.has(received.token)) return { side: 'sell', token: sent.token, quote: received.token };
    return { side: 'swap', from: sent.token, to: received.token };
  }
  return { side: 'unknown' };
}

function classifyOneInch(tx) {
  const sent = tx.transfers.find((t) => t.from === tx.wallet);
  const received = tx.transfers.find((t) => t.to === tx.wallet);
  // 1inch refunds unspent ETH, so ETH coming back does not make an ETH-paid swap a sell.
  if (Number(tx.value) > 0) return { side: 'buy', token: received.token, quote: 'ETH' };
  if (!received) return { side: 'sell', token: sent.token, quote: 'ETH' };
  if (QUOTES.has(sent.token)) return { side: 'buy', token: received.token, quote: sent.token };
  if (QUOTES.has(received.token)) return { side: 'sell', token: sent.token, quote: received.token };
  return { side: 'swap', from: sent.token, to: received.token };
}
