import type { FastifyInstance } from "fastify";
import { getOrder, listOrders } from "../services/orders.js";

export default async function orders(app: FastifyInstance) {
  app.get<{ Querystring: { status?: "pending" | "paid" | "shipped"; limit?: number } }>("/orders", {
    schema: {
      tags: ["orders"],
      summary: "List orders",
      querystring: {
        type: "object",
        properties: {
          status: { type: "string", enum: ["pending", "paid", "shipped"] },
          limit: { type: "integer", maximum: 100 },
        },
      },
      response: { 200: { description: "A page of orders, newest first", type: "array", items: { type: "object" } } },
    },
  }, async (req) => listOrders(req.query));

  app.get<{ Params: { id: string } }>("/orders/:id", {
    schema: {
      tags: ["orders"],
      summary: "Get an order",
      params: { type: "object", required: ["id"], properties: { id: { type: "string" } } },
      response: {
        200: { description: "The order", type: "object" },
        404: { description: "No order with this ID", type: "object" },
      },
    },
  }, async (req, reply) => (await getOrder(req.params.id)) ?? reply.code(404).send({ error: "not_found" }));
}
