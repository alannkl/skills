import Anthropic from "@anthropic-ai/sdk";
import { buildSystemPrompt } from "./prompt";
import { tools } from "./tools";
import type { Customer } from "../types";

const client = new Anthropic();

export async function reply(customer: Customer, history: Anthropic.MessageParam[], kb: string[]) {
  return client.messages.create({
    model: "claude-haiku-4-5",
    max_tokens: 600,
    system: buildSystemPrompt(customer, kb),
    tools,
    messages: history,
  });
}
