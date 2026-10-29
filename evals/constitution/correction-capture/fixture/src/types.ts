export interface Turn { role: "user" | "assistant"; text: string }
export interface ModelClient { complete(req: { system: string; user: string }): Promise<string> }
export interface MemoryStore { add(entry: { kind: "correction"; text: string; lesson: string }): Promise<void> }
