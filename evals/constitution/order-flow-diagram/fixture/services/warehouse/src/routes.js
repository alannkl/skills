import express from "express";
import { stock, reservations, shipments } from "./store.js";

export const router = express.Router();

router.get("/stock", async (req, res) => {
  res.json(await stock.levels(String(req.query.skus ?? "").split(",").filter(Boolean)));
});

router.post("/reservations", async (req, res) => {
  res.status(201).json(await reservations.create(req.body.orderId, req.body.items));
});

router.post("/shipments", async (req, res) => {
  res.status(201).json(await shipments.create(req.body.orderId, req.body.reservationId));
});
