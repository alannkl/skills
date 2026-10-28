// Every caller is an internal service with a shared API key.
export function requireApiKey(req, res, next) {
  if (req.get('x-api-key') !== process.env.API_KEY) return res.status(401).end();
  next();
}
