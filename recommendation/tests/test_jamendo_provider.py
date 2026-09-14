import httpx

from recommendation_engine.providers.jamendo_provider import JamendoProvider
from recommendation_engine.types import MusicQuery

_FAKE_RESPONSE = {
    "results": [
        {
            "name": "Sunset Drive",
            "artist_name": "Some Artist",
            "shareurl": "https://jamendo.com/track/123",
            "image": "https://jamendo.com/image/123.jpg",
            "audio": "https://mp3.jamendo.com/track/123.mp3",
        },
        {
            "name": "Night Walk",
            "artist_name": "Another Artist",
            "shareurl": "https://jamendo.com/track/456",
            "image": None,
            "audio": "https://mp3.jamendo.com/track/456.mp3",
        },
    ]
}


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._payload


def test_search_builds_request_and_maps_results(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["url"] = url
        captured["params"] = params
        return _FakeResponse(_FAKE_RESPONSE)

    monkeypatch.setattr(httpx, "get", fake_get)

    provider = JamendoProvider(client_id="test-client-id")
    query = MusicQuery(seed_genres=["ambient", "chill"], keywords=["calm", "soothing"], limit=5)
    tracks = provider.search(query)

    assert captured["url"] == "https://api.jamendo.com/v3.0/tracks/"
    assert captured["params"]["client_id"] == "test-client-id"
    assert captured["params"]["search"] == "calm soothing"
    assert captured["params"]["tags"] == "ambient,chill"
    assert captured["params"]["limit"] == 5

    assert len(tracks) == 2
    assert tracks[0].title == "Sunset Drive"
    assert tracks[0].artist == "Some Artist"
    assert tracks[0].provider == "jamendo"
    assert tracks[0].preview_url == "https://mp3.jamendo.com/track/123.mp3"
    assert tracks[1].album_art_url is None
