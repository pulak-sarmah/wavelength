import httpx

from recommendation_engine.providers.jamendo_provider import JamendoProvider
from recommendation_engine.types import MusicQuery

_TRACK = {
    "name": "Sunset Drive",
    "artist_name": "Some Artist",
    "shareurl": "https://jamendo.com/track/123",
    "image": "https://jamendo.com/image/123.jpg",
    "audio": "https://mp3.jamendo.com/track/123.mp3",
}


class _FakeResponse:
    def __init__(self, results: list[dict]):
        self._results = results

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return {"results": self._results}


def test_search_uses_single_tag_per_request_not_comma_joined(monkeypatch):
    """Jamendo's `tags` param ANDs multiple values together, so we must
    never send seed_genres as one comma-joined string (see module
    docstring) — each genre gets its own request."""
    seen_tags = []

    def fake_get(url, params=None, timeout=None):
        seen_tags.append(params.get("tags"))
        return _FakeResponse([_TRACK])

    monkeypatch.setattr(httpx, "get", fake_get)

    provider = JamendoProvider(client_id="test-client-id")
    query = MusicQuery(seed_genres=["ambient", "chill"], keywords=["calm"], limit=5)
    tracks = provider.search(query)

    assert seen_tags[0] == "ambient"  # first genre tried, succeeded immediately
    assert len(tracks) == 1
    assert tracks[0].title == "Sunset Drive"
    assert tracks[0].preview_url == "https://mp3.jamendo.com/track/123.mp3"


def test_search_falls_through_to_next_genre_when_one_is_empty(monkeypatch):
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(params.get("tags"))
        # "ambient" (tried 3x for retries) never has results; "chill" does.
        if params.get("tags") == "chill":
            return _FakeResponse([_TRACK])
        return _FakeResponse([])

    monkeypatch.setattr(httpx, "get", fake_get)

    provider = JamendoProvider(client_id="test-client-id")
    query = MusicQuery(seed_genres=["ambient", "chill"], keywords=[], limit=5)
    tracks = provider.search(query)

    assert calls.count("ambient") == 3  # 1 attempt + 2 retries, per _RETRIES_PER_TAG
    assert "chill" in calls
    assert len(tracks) == 1


def test_search_falls_back_to_no_tag_when_every_genre_is_empty(monkeypatch):
    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(params.get("tags"))
        if params.get("tags") is None:
            return _FakeResponse([_TRACK])
        return _FakeResponse([])

    monkeypatch.setattr(httpx, "get", fake_get)

    provider = JamendoProvider(client_id="test-client-id")
    query = MusicQuery(seed_genres=["ambient"], keywords=[], limit=5)
    tracks = provider.search(query)

    assert None in calls
    assert len(tracks) == 1
