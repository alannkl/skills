import jwt from 'jsonwebtoken';

const SECRET = process.env.JWT_SECRET;

export function signToken(user) {
  return jwt.sign({ sub: user.id, role: user.role }, SECRET, { expiresIn: '15m' });
}

export function verifyToken(token) {
  return jwt.verify(token, SECRET);
}
