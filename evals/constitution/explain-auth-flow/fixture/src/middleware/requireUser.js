export function requireUser(req, res, next) {
  if (!req.session.userId) return res.status(401).json({ error: 'not signed in' });
  next();
}

export function requireRole(role) {
  return (req, res, next) => {
    if (req.session.role !== role) return res.status(403).json({ error: 'forbidden' });
    next();
  };
}
