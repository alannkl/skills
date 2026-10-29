import { Gateway } from './gateway';

// Reads the stored history of a session after its run and keeps the turns since the case's prompt.
export async function collectTranscript(gw: Gateway, sessionName: string, caseId: string) {
  const history = await gw.sessions.history(sessionName);
  const start = history.findLastIndex((m) => m.role === 'user');
  return { caseId, messages: history.slice(start) };
}
