import express from "express";
import { router } from "./api/routes";

const app = express();
app.use(express.json());
app.use(router);
app.listen(Number(process.env.PORT ?? 3000));
