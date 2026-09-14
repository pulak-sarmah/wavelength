from pydantic import BaseModel

from app.schemas.vibe import VibeProfile


class TrackDTO(BaseModel):
    title: str
    artist: str
    provider: str
    external_url: str | None = None
    album_art_url: str | None = None
    preview_url: str | None = None


class RecommendationResponse(BaseModel):
    vibe: VibeProfile
    tracks: list[TrackDTO]
    explanation: str
