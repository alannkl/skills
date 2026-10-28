import { createServer } from 'node:http';
import { config } from './config.js';
import { charge } from './clients/payments.js';

createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/checkout') {
    const result = await charge('cus_demo', 4900, crypto.randomUUID());
    res.end(JSON.stringify(result));
    return;
  }
  res.statusCode = 404;
  res.end();
}).listen(config.port);
