// Cheap first pass: an obvious correction is captured without a reviewer call.
const CORRECTION_PHRASES = [
  "that's wrong",
  "you're wrong",
  "not what i asked",
  "i told you",
  "don't do that",
  "stop doing",
];

export function isObviousCorrection(text: string): boolean {
  const lower = text.toLowerCase();
  return CORRECTION_PHRASES.some((phrase) => lower.includes(phrase));
}
