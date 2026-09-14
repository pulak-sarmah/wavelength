"""Orchestrates the full pipeline for one request:

    text -> vibe_ml.predict_vibe -> RecommendationEngine.recommend -> persist

This is the only place in apps/api that calls both vibe_ml and
recommendation_engine — routes stay thin and just call this service.

`context` (time of day) is not part of vibe_ml's output — text essentially
never states time of day, so it's read off the request's own clock instead
of being predicted. See docs/ml-plan.md.
"""

from datetime import datetime, time

from recommendation_engine import RecommendationEngine
from recommendation_engine.providers.base import MusicProvider
from recommendation_engine.providers.jamendo_provider import JamendoProvider
from recommendation_engine.providers.mock_provider import MockMusicProvider
from sqlalchemy.orm import Session
from vibe_ml import predict_vibe

from app.core.config import settings
from app.db.models import VibeQuery
from app.schemas.recommendation import RecommendationResponse, TrackDTO
from app.schemas.vibe import VibeProfile


def _build_provider() -> MusicProvider:
    if settings.music_provider == "jamendo" and settings.jamendo_client_id:
        return JamendoProvider(client_id=settings.jamendo_client_id)
    # Falls back to the mock provider whenever a real one isn't configured,
    # rather than hard-failing — see .env.example.
    return MockMusicProvider()


_engine = RecommendationEngine(provider=_build_provider())

_MORNING_START = time(5, 0)
_AFTERNOON_START = time(12, 0)
_EVENING_START = time(17, 0)
_NIGHT_START = time(21, 0)


def context_from_time(dt: datetime) -> str:
    """Map a wall-clock time to a coarse time-of-day context bucket."""
    t = dt.time()
    if _MORNING_START <= t < _AFTERNOON_START:
        return "morning"
    if _AFTERNOON_START <= t < _EVENING_START:
        return "afternoon"
    if _EVENING_START <= t < _NIGHT_START:
        return "evening"
    return "night"


def get_vibe_recommendation(
    text: str, preferences: dict | None = None, db: Session | None = None
) -> RecommendationResponse:
    prediction = predict_vibe(text)
    vibe = VibeProfile(
        mood=prediction.mood,
        energy=prediction.energy,
        valence=prediction.valence,
        context=context_from_time(datetime.now()),
        social_energy=prediction.social_energy,
        vibe_tags=prediction.vibe_tags,
        confidence=prediction.confidence,
    )

    tracks = _engine.recommend(prediction, preferences)

    if db is not None:
        db.add(
            VibeQuery(
                text=text,
                mood=vibe.mood,
                energy=vibe.energy,
                valence=vibe.valence,
                context=vibe.context,
                social_energy=vibe.social_energy,
                confidence=vibe.confidence,
            )
        )
        db.commit()

    return RecommendationResponse(
        vibe=vibe,
        tracks=[
            TrackDTO(
                title=track.title,
                artist=track.artist,
                provider=track.provider,
                external_url=track.external_url,
                album_art_url=track.album_art_url,
                preview_url=track.preview_url,
            )
            for track in tracks
        ],
        explanation=_explain(vibe),
    )


def _explain(vibe: VibeProfile) -> str:
    # vibe_tags[0] is always the mood name itself (see MOOD_TO_DERIVED) —
    # skip it so the sentence doesn't repeat the mood twice.
    descriptive_tags = [tag for tag in vibe.vibe_tags if tag != vibe.mood]
    tag = descriptive_tags[0] if descriptive_tags else vibe.mood
    return f"Based on your {vibe.mood} mood, {vibe.energy} energy, and {tag} vibe."
