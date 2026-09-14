"""Vibe profile -> MusicQuery, then fan out to the configured MusicProvider.

This is the only place that decides how a vibe maps to search parameters.
It is intentionally rule-based and explainable for the first version (see
docs/recommendation-system.md) — a learned ranking model can replace the
heuristic later without changing this class's public interface.
"""

from dataclasses import dataclass

from vibe_ml import VibePrediction

from recommendation_engine.genres import ENERGY_TO_TARGET, MOOD_TO_GENRES, VALENCE_TO_TARGET
from recommendation_engine.providers.base import MusicProvider
from recommendation_engine.types import MusicQuery, TrackResult

DEFAULT_LIMIT = 10


@dataclass
class RecommendationEngine:
    provider: MusicProvider

    def build_query(self, prediction: VibePrediction, preferences: dict | None = None) -> MusicQuery:
        """Translate a vibe profile (+ optional user preferences) into a
        provider-agnostic MusicQuery.

        A user-supplied `preferences["genres"]` fully overrides the
        mood-derived genre list; `preferences["limit"]` overrides the
        default result count. `prediction.confidence` isn't used yet (e.g.
        to broaden the query on low-confidence predictions) — a future
        enhancement, not needed for a first working version.
        """
        preferences = preferences or {}
        seed_genres = list(preferences.get("genres") or MOOD_TO_GENRES[prediction.mood])
        return MusicQuery(
            seed_genres=seed_genres,
            keywords=list(prediction.vibe_tags),
            target_energy=ENERGY_TO_TARGET[prediction.energy],
            target_valence=VALENCE_TO_TARGET[prediction.valence],
            limit=preferences.get("limit", DEFAULT_LIMIT),
        )

    def recommend(self, prediction: VibePrediction, preferences: dict | None = None) -> list[TrackResult]:
        query = self.build_query(prediction, preferences)
        return self.provider.search(query)
