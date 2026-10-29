import type { Request, Response } from "express";
import { z } from "zod";
import { requireAuth } from "../auth";
import { ApiError } from "../errors";
import { log } from "../log";
import { db } from "../../db";

const listQuery = z.object({ status: z.enum(["draft", "open", "paid"]).optional() });

export async function listInvoices(req: Request, res: Response) {
  const user = requireAuth(req);
  const query = listQuery.parse(req.query);
  log.info({ requestId: req.id, route: "GET /invoices" });
  res.json(await db.invoices.list(user.accountId, query));
}

export async function getInvoice(req: Request, res: Response) {
  const user = requireAuth(req);
  const invoice = await db.invoices.find(user.accountId, req.params.id);
  if (!invoice) throw new ApiError(404, "invoice_not_found", "No invoice with that ID");
  log.info({ requestId: req.id, route: "GET /invoices/:id" });
  res.json(invoice);
}
