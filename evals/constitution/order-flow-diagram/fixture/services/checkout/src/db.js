import pg from "pg";

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

export const orders = {
  async create({ customerId, items, status }) {
    const { rows } = await pool.query(
      "INSERT INTO orders (customer_id, items, status) VALUES ($1, $2, $3) RETURNING id",
      [customerId, JSON.stringify(items), status],
    );
    return rows[0];
  },
  async update(id, fields) {
    const keys = Object.keys(fields);
    const sets = keys.map((k, i) => `${k.replace(/[A-Z]/g, (c) => "_" + c.toLowerCase())} = $${i + 2}`);
    await pool.query(`UPDATE orders SET ${sets.join(", ")} WHERE id = $1`, [id, ...keys.map((k) => fields[k])]);
  },
};
