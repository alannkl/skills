export interface Message { role: 'user' | 'assistant' | 'tool'; text: string }

export interface Session {
  send(text: string): Promise<void>;
  waitForIdle(opts: { timeoutMs: number }): Promise<void>;
}

export interface Gateway {
  sessions: {
    get(name: string): Promise<Session>;        // creates the session on first use
    create(name: string): Promise<Session>;
    reset(name: string): Promise<void>;         // clears history and memory, keeps the session
    delete(name: string): Promise<void>;        // removes the session and its stored history
    history(name: string): Promise<Message[]>;
  };
}
