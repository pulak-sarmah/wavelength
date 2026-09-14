// Mood -> aurora gradient, used by the 3D particle field and the vibe orb.
// Mirrors the spirit of ml/src/vibe_ml/labels.py's MOOD_TO_DERIVED — a
// fixed, hand-tuned table, not decoration. Colors are the two ends of a
// gradient the 3D layer interpolates across.

import type { Mood, Energy, Valence } from "@vibe/shared";

export interface AuroraGradient {
  from: string;
  to: string;
}

export const MOOD_TO_GRADIENT: Record<Mood, AuroraGradient> = {
  happy: { from: "#FFB84D", to: "#FF6B9D" },
  sad: { from: "#3B4CCA", to: "#6E5BFF" },
  calm: { from: "#4FD1C5", to: "#6EE7B7" },
  anxious: { from: "#F59E0B", to: "#EF4444" },
  angry: { from: "#E11D48", to: "#BE123C" },
  excited: { from: "#FF3D9A", to: "#FFD23F" },
  romantic: { from: "#C77DFF", to: "#FF8FE3" },
  nostalgic: { from: "#D4A373", to: "#9C6644" },
  neutral: { from: "#9C97B8", to: "#6E5BFF" },
};

// Idle state before any vibe has been analyzed — a quiet, slow drift.
export const IDLE_GRADIENT: AuroraGradient = { from: "#4C4A6E", to: "#6E5BFF" };

export const ENERGY_TO_INTENSITY: Record<Energy, number> = {
  very_low: 0.15,
  low: 0.35,
  medium: 0.55,
  high: 0.75,
  very_high: 0.95,
};

export const VALENCE_TO_WARMTH: Record<Valence, number> = {
  negative: 0.2,
  neutral: 0.5,
  positive: 0.8,
};
