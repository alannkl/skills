import { TideChart } from "@/components/TideChart";
import { getTides } from "@/lib/api";

export default async function HomePage() {
  const tides = await getTides("SFO");
  return <TideChart tides={tides} />;
}
