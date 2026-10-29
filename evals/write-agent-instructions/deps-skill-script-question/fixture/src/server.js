import express from "express";
import { z } from "zod";
import { postEntry, listEntries } from "./ledger.js";

const app = express();
app.use(express.json());

const Entry = z.object({
  account: z.string().min(1),
  amountCents: z.number().int(),
  memo: z.string().optional(),
});

app.post("/entries", async (req, res) => {
  const parsed = Entry.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error.flatten());
  res.status(201).json(await postEntry(parsed.data));
});

app.get("/accounts/:account/entries", async (req, res) => {
  res.json(await listEntries(req.params.account));
});

app.listen(process.env.PORT ?? 3000);
