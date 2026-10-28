import express from 'express';
import session from 'express-session';
import { RedisStore } from 'connect-redis';
import { createClient } from 'redis';
import login from './routes/login.js';
import projects from './routes/projects.js';

const redis = createClient({ url: process.env.REDIS_URL });
await redis.connect();

const app = express();
app.use(express.json());
app.use(session({
  store: new RedisStore({ client: redis, prefix: 'sess:' }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 1000 * 60 * 60 * 24 * 14 },
}));

app.use(login);
app.use('/api/projects', projects);

app.listen(process.env.PORT ?? 3000);
