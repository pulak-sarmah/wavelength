// Mirrors packages/shared/schemas/track.schema.json

import type { VibeProfile } from "./vibe";

export interface Track {
  title: string;
  artist: string;
  provider: string;
  external_url: string | null;
  album_art_url: string | null;
  preview_url: string | null;
}

export interface RecommendationResponse {
  vibe: VibeProfile;
  tracks: Track[];
  explanation: string;
}
