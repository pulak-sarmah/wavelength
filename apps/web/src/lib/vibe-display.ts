import type { Mood } from "@vibe/shared";

// A more evocative phrase than the raw mood label for the reveal moment —
// the 3D orb already carries the visual identity, so this stays understated
// rather than duplicating it with an icon/emoji.
export const MOOD_TO_DISPLAY_NAME: Record<Mood, string> = {
  happy: "Bright & joyful",
  sad: "Quiet & reflective",
  calm: "Calm & grounded",
  anxious: "Restless & uneasy",
  angry: "Charged & intense",
  excited: "Electric & alive",
  romantic: "Warm & tender",
  nostalgic: "Wistful & faraway",
  neutral: "Easy & even",
};
