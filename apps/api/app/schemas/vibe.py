"""API request/response contracts for the vibe endpoint.

Mirrors the shape defined in packages/shared/schemas/vibe-profile.schema.json
— keep the two in sync.
"""

from pydantic import BaseModel


class VibeRequest(BaseModel):
    text: str
    preferences: dict | None = None
    # Optional photo is accepted as a separate multipart field on the route,
    # not as part of this JSON body — see app/api/routes/vibe.py.


class VibeProfile(BaseModel):
    mood: str
    energy: str
    valence: str
    context: str
    social_energy: str
    vibe_tags: list[str]
    confidence: float
