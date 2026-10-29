import type { FastifyInstance } from "fastify";
import { handleStripeEvent } from "../services/stripe.js";

export default async function webhooks(app: FastifyInstance) {
  app.post("/webhooks/stripe", async (req, reply) => {
    await handleStripeEvent(req.headers["stripe-signature"], req.body);
    return reply.code(204).send();
  });
}
