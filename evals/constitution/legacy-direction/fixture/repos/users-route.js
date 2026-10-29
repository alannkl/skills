const express = require('express');
const users = require('../repos/users');

const router = express.Router();

router.get('/:id', async (req, res, next) => {
  try {
    const user = await users.findUser(req.params.id);
    if (!user) return res.status(404).json({ error: 'not found' });
    res.json(user);
  } catch (err) {
    next(err);
  }
});

module.exports = router;
