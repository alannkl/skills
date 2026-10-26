import { CAPTURE_PROMPT } from "./capturePrompt";

export type MemoryItem = { kind: "preference" | "fact" | "correction"; text: string };

const KINDS = new Set(["preference", "fact", "correction"]);

/** Parses the <memory> block at the end of a reply; lines with an unknown kind are dropped. */
export function parseMemory(reply: string): MemoryItem[] {
  const match = reply.match(/<memory>([\s\S]*?)<\/memory>\s*$/);
  if (!match) return [];
  return match[1]
    .split("\n")
    .map((line) => line.trim().replace(/^-\s*/, ""))
    .map((line) => line.match(/^(\w+):\s*(.+)$/))
    .filter((m): m is RegExpMatchArray => m !== null && KINDS.has(m[1]))
    .map((m) => ({ kind: m[1] as MemoryItem["kind"], text: m[2] }));
}

export function systemPromptWithMemory(base: string, known: string[]): string {
  const knownBlock = known.length ? known.map((k) => `- ${k}`).join("\n") : "(nothing yet)";
  return `${base}\n\n## What you know about the user\n\n${knownBlock}\n${CAPTURE_PROMPT}`;
}
