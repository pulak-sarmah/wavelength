"""Jamendo-backed MusicProvider.

Jamendo (https://www.jamendo.com) hosts Creative Commons-licensed tracks
and — unlike Spotify's OAuth-gated, preview-URL-deprecated API — its free
`client_id`-only search endpoint returns a direct, legally streamable
full-track audio URL right in the response. That's what makes it a good
fit for `TrackResult.preview_url` without any auth flow.

Get a free client_id at https://devportal.jamendo.com and set
JAMENDO_CLIENT_ID in .env — see apps/api/.env.example.

Two things learned from testing against the real API (not assumptions):

1. `tags` is a single-genre filter, not an OR list — passing multiple
   comma-separated tags requires a track to match *all* of them
   simultaneously, which is so narrow it usually returns nothing. We try
   each of `query.seed_genres` as its own request instead, falling
   through to the next genre (then to no filter at all) if one comes back
   empty.
2. Jamendo's `search` does literal text matching against track/artist
   names — it is not a semantic/mood filter, so `query.keywords`
   (semantic tags like "calm", "energetic") were never a meaningful fit
   for it and are not sent. `seed_genres` (real genre tags) are the only
   part of MusicQuery this provider can act on.
3. The API is genuinely flaky at the network/backend level: the *exact
   same* single-tag request, repeated back to back, returns a full page
   of results about half the time and zero the other half. This isn't
   caused by our query shape — a few retries per tag are needed before
   concluding a genre truly has no results.
"""

import httpx

from recommendation_engine.providers.base import MusicProvider
from recommendation_engine.types import MusicQuery, TrackResult

_API_URL = "https://api.jamendo.com/v3.0/tracks/"
_RETRIES_PER_TAG = 2


class JamendoProvider(MusicProvider):
    def __init__(self, client_id: str, timeout: float = 5.0) -> None:
        self.client_id = client_id
        self.timeout = timeout

    def search(self, query: MusicQuery) -> list[TrackResult]:
        # target_energy/target_valence have no equivalent in Jamendo's
        # search API (no audio-features endpoint like Spotify's) — not
        # used here, not silently pretended to be honored.
        for tag in query.seed_genres:
            results = self._fetch(tag, query.limit)
            if results:
                return [self._to_track_result(item) for item in results]

        # No genre came back with anything (including after retries) —
        # last resort so the UI never shows zero tracks for a real query.
        results = self._fetch(None, query.limit)
        return [self._to_track_result(item) for item in results]

    def _fetch(self, tag: str | None, limit: int) -> list[dict]:
        params = {"client_id": self.client_id, "format": "json", "limit": limit}
        if tag:
            params["tags"] = tag

        for _attempt in range(_RETRIES_PER_TAG + 1):
            response = httpx.get(_API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            results = response.json().get("results", [])
            if results:
                return results
        return []

    @staticmethod
    def _to_track_result(item: dict) -> TrackResult:
        return TrackResult(
            title=item["name"],
            artist=item["artist_name"],
            provider="jamendo",
            external_url=item.get("shareurl"),
            album_art_url=item.get("image"),
            preview_url=item.get("audio"),
        )
