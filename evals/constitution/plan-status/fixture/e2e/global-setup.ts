import { execSync } from 'node:child_process';

// Brings the test stack up before the suite and waits until every service is healthy.
export default async function globalSetup() {
  execSync('docker compose -f docker-compose.test.yml up -d --wait', { stdio: 'inherit' });
  return async () => {
    execSync('docker compose -f docker-compose.test.yml down -v', { stdio: 'inherit' });
  };
}
