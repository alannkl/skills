const express = require('express');
const jwt = require('jsonwebtoken');
const { checkPassword } = require('./users');

const app = express();
app.use(express.json());

app.post('/auth/token', async (req, res) => {
  const user = await checkPassword(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: 'bad credentials' });
  res.json({ token: jwt.sign({ sub: user.id }, process.env.JWT_SECRET, { expiresIn: '24h' }) });
});

app.use((req, res, next) => {
  const token = (req.headers.authorization || '').replace(/^Bearer /, '');
  try {
    req.userId = jwt.verify(token, process.env.JWT_SECRET).sub;
    next();
  } catch {
    res.status(401).json({ error: 'not signed in' });
  }
});

app.use('/notes', require('./notes'));
app.listen(process.env.PORT || 3000);
