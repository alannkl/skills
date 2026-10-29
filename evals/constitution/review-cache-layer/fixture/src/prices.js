const db = require('./db');
const { cached } = require('./cache');

// Price of a product in the shopper's currency, in minor units.
async function getPrice(productId, currency) {
  return cached(`price:${productId}`, async () => {
    const rows = await db.query(
      'SELECT amount FROM prices WHERE product_id = $1 AND currency = $2', [productId, currency]);
    return rows.length ? rows[0].amount : null;
  });
}

// Called by the admin panel when a merchandiser changes a price.
async function setPrice(productId, currency, amount) {
  await db.query(
    'UPDATE prices SET amount = $3 WHERE product_id = $1 AND currency = $2', [productId, currency, amount]);
}

module.exports = { getPrice, setPrice };
