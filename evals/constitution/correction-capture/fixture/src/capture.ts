import { isObviousCorrection } from "./prefilter.js";
import { review } from "./reviewer.js";
import type { ModelClient, MemoryStore, Turn } from "./types.js";

export async function onUserMessage(text: string, recent: Turn[], client: ModelClient, memory: MemoryStore) {
  if (isObviousCorrection(text)) {
    await memory.add({ kind: "correction", text, lesson: "" });
    return;
  }
  const verdict = await review(client, text, recent);
  if (verdict.isCorrection) {
    await memory.add({ kind: "correction", text, lesson: verdict.lesson });
  }
}
