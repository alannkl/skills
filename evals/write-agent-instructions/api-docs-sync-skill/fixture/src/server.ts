import Fastify from "fastify";
import autoload from "@fastify/autoload";
import { fileURLToPath } from "node:url";

const app = Fastify({ logger: true });
await app.register(autoload, { dir: fileURLToPath(new URL("./routes", import.meta.url)) });
await app.listen({ port: Number(process.env.PORT ?? 3000) });
