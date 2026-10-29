import { Gateway } from './gateway';
import { collectTranscript } from './transcripts';

export interface Case { id: string; prompt: string }

// Each worker keeps one named session on the gateway and reuses it for every case.
export async function runCase(gw: Gateway, worker: string, c: Case) {
  const session = await gw.sessions.get(`eval-${worker}`);
  await session.send(c.prompt);
  await session.waitForIdle({ timeoutMs: 15 * 60_000 });
  return collectTranscript(gw, `eval-${worker}`, c.id);
}
