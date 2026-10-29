const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');
const { checkPassword } = require('./users');

const redis = createClient({ url: process.env.REDIS_URL });
redis.connect();

const app = express();
app.use(express.json());
app.use(session({
  name: 'sid',
  store: new RedisStore({ client: redis }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, sameSite: 'lax', secure: process.env.NODE_ENV === 'production', maxAge: 7 * 24 * 3600 * 1000 },
}));

app.post('/login', async (req, res) => {
  const user = await checkPassword(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: 'bad credentials' });
  req.session.regenerate(() => {
    req.session.userId = user.id;
    res.status(204).end();
  });
});

app.post('/logout', (req, res) => req.session.destroy(() => res.status(204).end()));

app.use((req, res, next) => {
  if (!req.session.userId) return res.status(401).json({ error: 'not signed in' });
  req.userId = req.session.userId;
  next();
});

app.use('/notes', require('./notes'));
app.listen(process.env.PORT || 3000);
