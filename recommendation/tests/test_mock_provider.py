from recommendation_engine.providers.mock_provider import MockMusicProvider
from recommendation_engine.types import MusicQuery


def test_mock_provider_respects_limit():
    provider = MockMusicProvider()
    results = provider.search(MusicQuery(limit=2))
    assert len(results) == 2
    assert all(track.provider == "mock" for track in results)
