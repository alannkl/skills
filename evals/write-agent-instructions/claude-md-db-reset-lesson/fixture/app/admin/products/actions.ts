"use server";

import { prisma } from "@/lib/db";
import { revalidatePath } from "next/cache";

export async function updateStock(productId: string, stock: number) {
  await prisma.product.update({ where: { id: productId }, data: { stock } });
  revalidatePath("/admin/products");
}
