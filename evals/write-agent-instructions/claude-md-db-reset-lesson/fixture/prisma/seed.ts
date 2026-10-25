import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  await prisma.product.createMany({
    data: [
      { slug: "logo-tee", name: "Logo Tee", priceCents: 2400, stock: 40 },
      { slug: "enamel-pin", name: "Enamel Pin", priceCents: 800, stock: 120 },
      { slug: "tote", name: "Canvas Tote", priceCents: 1800, stock: 25 },
    ],
    skipDuplicates: true,
  });
}

main().finally(() => prisma.$disconnect());
