// Thin fetch wrapper around apps/api. Kept as the single place that knows
// the backend's base URL and endpoint shapes — components should call
// these functions, never fetch() directly.

import type { RecommendationResponse } from "@vibe/shared";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getVibeRecommendation(
  text: string,
  preferences?: Record<string, unknown>
): Promise<RecommendationResponse> {
  const res = await fetch(`${API_URL}/vibe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, preferences }),
  });

  if (!res.ok) {
    throw new Error(`Vibe request failed: ${res.status}`);
  }

  return res.json();
}
