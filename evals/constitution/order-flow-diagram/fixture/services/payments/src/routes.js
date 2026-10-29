import express from "express";
import { chargeCard } from "./stripe.js";

export const router = express.Router();

router.post("/charges", async (req, res) => {
  const result = await chargeCard(req.body, req.get("idempotency-key"));
  if (result.declined) return res.status(402).json({ reason: result.reason });
  res.status(201).json({ id: result.id });
});
