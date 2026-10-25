import { readdirSync } from "node:fs";

// Every folder in skills/ is offered to the agent; the model picks skills by description.
export function skillList(dir = "skills"): string[] {
  return readdirSync(dir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);
}
