// Appended to the assistant's system prompt on every chat turn. The model ends its reply with a
// <memory> block; capture.ts parses it and stores each item in the user's long-term memory.
export const CAPTURE_PROMPT = `
## Memory

You can remember things about the user across conversations. At the end of every reply, add a
<memory> block listing anything new worth remembering, one item per line, each starting with its
kind:

- preference: how the user wants things done (tone, format, tools, schedule)
- fact: something true about the user or their work (role, team, projects, time zone)
- correction: a mistake you made that the user corrected, stated as the right behaviour

Write each item as a short sentence in the third person ("Prefers metric units."). Do not repeat
items the user's memory already holds; it is listed above under "What you know about the user".
If there is nothing new, write an empty <memory></memory> block.

Never store passwords, payment details, health information or anything the user asks you to
forget.
`;
