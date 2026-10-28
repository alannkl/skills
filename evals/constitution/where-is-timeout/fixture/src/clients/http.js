import { config } from '../config.js';

// Shared client for internal services: shipping, inventory, email.
export async function request(url, options = {}) {
  let lastError;
  for (let attempt = 0; attempt <= config.http.retries; attempt++) {
    try {
      return await fetch(url, { ...options, signal: AbortSignal.timeout(config.http.timeoutMs) });
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}
