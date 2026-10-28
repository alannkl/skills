import express from 'express';
import { requireApiKey } from './auth.js';
import customers from './routes/customers.js';
import payments from './routes/payments.js';

const app = express();
app.use(express.json());
app.use(requireApiKey);
app.use('/customers', customers);
app.use('/payments', payments);
app.listen(process.env.PORT ?? 3000);
