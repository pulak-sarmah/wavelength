// Mirrors packages/shared/schemas/vibe-profile.schema.json
// and apps/api/app/schemas/vibe.py — keep all three in sync.

export type Mood =
  | "happy"
  | "sad"
  | "calm"
  | "anxious"
  | "angry"
  | "excited"
  | "romantic"
  | "nostalgic"
  | "neutral";

export type Energy = "very_low" | "low" | "medium" | "high" | "very_high";

export type Valence = "negative" | "neutral" | "positive";

export type VibeContext = "morning" | "afternoon" | "evening" | "night" | "unknown";

export type SocialEnergy = "low" | "medium" | "high";

export interface VibeProfile {
  mood: Mood;
  energy: Energy;
  valence: Valence;
  context: VibeContext;
  social_energy: SocialEnergy;
  vibe_tags: string[];
  confidence: number;
}
