from vibe_ml import VibePrediction

from recommendation_engine.engine import RecommendationEngine
from recommendation_engine.genres import MOOD_TO_GENRES
from recommendation_engine.providers.mock_provider import MockMusicProvider


def _prediction(**overrides) -> VibePrediction:
    defaults = dict(
        mood="sad",
        energy="low",
        valence="negative",
        social_energy="low",
        vibe_tags=["sad", "melancholic", "reflective"],
        confidence=0.9,
    )
    defaults.update(overrides)
    return VibePrediction(**defaults)


def test_build_query_uses_mood_derived_genres_and_targets():
    engine = RecommendationEngine(provider=MockMusicProvider())
    query = engine.build_query(_prediction())

    assert query.seed_genres == MOOD_TO_GENRES["sad"]
    assert query.keywords == ["sad", "melancholic", "reflective"]
    assert query.target_energy == 0.3
    assert query.target_valence == 0.2
    assert query.limit == 10


def test_build_query_preferences_override_genres_and_limit():
    engine = RecommendationEngine(provider=MockMusicProvider())
    query = engine.build_query(_prediction(), preferences={"genres": ["jazz"], "limit": 3})

    assert query.seed_genres == ["jazz"]
    assert query.limit == 3


def test_recommend_returns_tracks_from_provider():
    engine = RecommendationEngine(provider=MockMusicProvider())
    tracks = engine.recommend(_prediction(mood="happy", energy="high", valence="positive"))

    assert len(tracks) > 0
    assert all(track.provider == "mock" for track in tracks)
