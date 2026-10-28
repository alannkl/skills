import { Router } from 'express';
import bcrypt from 'bcrypt';
import { findUserByEmail } from '../db.js';

const router = Router();

router.post('/login', async (req, res) => {
  const user = await findUserByEmail(req.body.email);
  if (!user || !(await bcrypt.compare(req.body.password, user.passwordHash))) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  req.session.regenerate((err) => {
    if (err) return res.status(500).end();
    req.session.userId = user.id;
    req.session.role = user.role;
    res.json({ id: user.id });
  });
});

router.post('/logout', (req, res) => {
  req.session.destroy(() => res.status(204).end());
});

export default router;
