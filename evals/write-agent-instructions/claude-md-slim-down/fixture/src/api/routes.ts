import { Router } from "express";
import { getInvoice, listInvoices } from "./handlers/invoices";

export const PUBLIC_ROUTES = ["/health", "/webhooks/stripe"];

export const router = Router();
router.get("/invoices", listInvoices);
router.get("/invoices/:id", getInvoice);
