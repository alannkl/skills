import express from "express";
import { avatars } from "./routes/avatars.js";

const app = express();
app.use("/uploads", express.static("uploads"));
app.use("/avatars", avatars);
app.listen(process.env.PORT ?? 3000);
