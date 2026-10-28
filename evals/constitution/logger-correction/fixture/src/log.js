// Structured JSON logs; LOG_LEVEL sets the minimum level (default info).
const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };
const min = LEVELS[process.env.LOG_LEVEL ?? 'info'];

function write(level, msg, fields = {}) {
  if (LEVELS[level] < min) return;
  process.stdout.write(JSON.stringify({ time: new Date().toISOString(), level, msg, ...fields }) + '\n');
}

export const logger = {
  debug: (msg, fields) => write('debug', msg, fields),
  info: (msg, fields) => write('info', msg, fields),
  warn: (msg, fields) => write('warn', msg, fields),
  error: (msg, fields) => write('error', msg, fields),
};
