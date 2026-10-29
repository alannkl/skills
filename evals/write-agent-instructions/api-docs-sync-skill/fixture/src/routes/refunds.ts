import type { FastifyInstance } from "fastify";
import { createRefund } from "../services/refunds.js";

export default async function refunds(app: FastifyInstance) {
  app.post<{ Body: { order_id: string; amount_cents: number; reason?: string } }>("/refunds", {
    schema: {
      tags: ["refunds"],
      summary: "Refund an order",
      body: {
        type: "object",
        required: ["order_id", "amount_cents"],
        properties: {
          order_id: { type: "string" },
          amount_cents: { type: "integer" },
          reason: { type: "string" },
        },
      },
      response: {
        201: { description: "Refund created", type: "object" },
        409: { description: "Order already refunded", type: "object" },
      },
    },
  }, async (req, reply) => {
    const refund = await createRefund(req.body);
    return refund ? reply.code(201).send(refund) : reply.code(409).send({ error: "already_refunded" });
  });
}
