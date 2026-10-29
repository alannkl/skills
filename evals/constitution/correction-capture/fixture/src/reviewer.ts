import type { ModelClient, Turn } from "./types.js";

export const REVIEWER_PROMPT = `You review one user message in a conversation with an AI assistant.
Decide whether the message corrects the assistant. Corrections are messages such as:
- "that's wrong"
- "you're wrong about X"
- "that's not what I asked"
- "I told you to ..."
Reply with JSON: {"isCorrection": true | false, "lesson": "<what the assistant should do instead, or empty>"}.`;

export async function review(client: ModelClient, message: string, recent: Turn[]) {
  const transcript = recent.map((t) => `${t.role}: ${t.text}`).join("\n");
  const reply = await client.complete({
    system: REVIEWER_PROMPT,
    user: `Earlier turns:\n${transcript}\n\nMessage to review:\n${message}`,
  });
  return JSON.parse(reply) as { isCorrection: boolean; lesson: string };
}
