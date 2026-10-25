import type { Tide } from "@tidepool/shared";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:4000";

export async function getTides(station: string): Promise<Tide[]> {
  const res = await fetch(`${BASE}/tides/${station}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`tides ${res.status}`);
  return res.json();
}
