"""A fake MusicProvider for local development and tests, so the full
pipeline (ML -> engine -> provider -> API -> UI) can run end-to-end
before any real provider credentials exist.
"""

from recommendation_engine.providers.base import MusicProvider
from recommendation_engine.types import MusicQuery, TrackResult

_PLACEHOLDER_TRACKS = [
    TrackResult(title="Weightless", artist="Marconi Union", provider="mock"),
    TrackResult(title="Holocene", artist="Bon Iver", provider="mock"),
    TrackResult(title="Saturn", artist="Sleeping At Last", provider="mock"),
]


class MockMusicProvider(MusicProvider):
    def search(self, query: MusicQuery) -> list[TrackResult]:
        return _PLACEHOLDER_TRACKS[: query.limit]
