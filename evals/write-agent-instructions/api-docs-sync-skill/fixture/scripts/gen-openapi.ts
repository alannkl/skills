// Writes openapi.yaml from the route schemas in src/routes/.
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import autoload from "@fastify/autoload";
import swagger from "@fastify/swagger";
import Fastify from "fastify";
import pkg from "../package.json" with { type: "json" };

const app = Fastify();
await app.register(swagger, {
  openapi: { info: { title: "shopfront-api", version: pkg.version } },
  transform: ({ schema, url }) => ({ schema: schema?.response ? schema : { ...schema, hide: true }, url }),
});
await app.register(autoload, { dir: join(import.meta.dirname, "../src/routes") });
await app.ready();
writeFileSync("openapi.yaml", app.swagger({ yaml: true }));
