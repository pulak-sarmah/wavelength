"""Jamendo-backed MusicProvider.

Jamendo (https://www.jamendo.com) hosts Creative Commons-licensed tracks
and — unlike Spotify's OAuth-gated, preview-URL-deprecated API — its free
`client_id`-only search endpoint returns a direct, legally streamable
full-track audio URL right in the response. That's what makes it a good
fit for `TrackResult.preview_url` without any auth flow.

Get a free client_id at https://devportal.jamendo.com and set
JAMENDO_CLIENT_ID in .env — see apps/api/.env.example.
"""

import httpx

from recommendation_engine.providers.base import MusicProvider
from recommendation_engine.types import MusicQuery, TrackResult

_API_URL = "https://api.jamendo.com/v3.0/tracks/"


class JamendoProvider(MusicProvider):
    def __init__(self, client_id: str, timeout: float = 5.0) -> None:
        self.client_id = client_id
        self.timeout = timeout

    def search(self, query: MusicQuery) -> list[TrackResult]:
        params = {
            "client_id": self.client_id,
            "format": "json",
            "limit": query.limit,
            "search": " ".join(query.keywords),
            "tags": ",".join(query.seed_genres),
        }
        # target_energy/target_valence have no equivalent in Jamendo's
        # search API (no audio-features endpoint like Spotify's) — not
        # used here, not silently pretended to be honored.
        response = httpx.get(_API_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [self._to_track_result(item) for item in results]

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
