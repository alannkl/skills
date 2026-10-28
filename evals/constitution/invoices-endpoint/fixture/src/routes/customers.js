import { Router } from 'express';
import { query } from '../db/raw.js';

const router = Router();

router.get('/:id', async (req, res) => {
  const [customer] = await query('SELECT id, name, email, created_at FROM customers WHERE id = $1', [req.params.id]);
  if (!customer) return res.status(404).json({ error: 'customer not found' });
  res.json(customer);
});

router.patch('/:id', async (req, res) => {
  const [customer] = await query(
    'UPDATE customers SET name = coalesce($2, name), email = coalesce($3, email) WHERE id = $1 RETURNING id, name, email',
    [req.params.id, req.body.name, req.body.email],
  );
  if (!customer) return res.status(404).json({ error: 'customer not found' });
  res.json(customer);
});

export default router;
