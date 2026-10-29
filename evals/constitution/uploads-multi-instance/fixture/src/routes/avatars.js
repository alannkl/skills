import { Router } from "express";
import multer from "multer";
import { db } from "../db.js";

const upload = multer({ dest: "uploads/", limits: { fileSize: 2 * 1024 * 1024 } });
export const avatars = Router();

avatars.post("/", upload.single("avatar"), async (req, res) => {
  const url = `/uploads/${req.file.filename}`;
  await db.query("UPDATE members SET avatar_url = $1 WHERE id = $2", [url, req.user.id]);
  res.status(201).json({ url });
});
