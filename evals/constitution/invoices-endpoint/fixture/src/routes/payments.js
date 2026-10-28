import { Router } from 'express';
import * as payments from '../repos/payments.js';

const router = Router();

router.get('/invoice/:invoiceId', async (req, res) => {
  res.json(await payments.listByInvoice(req.params.invoiceId));
});

export default router;
