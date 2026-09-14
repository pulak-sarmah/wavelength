"""Provider-agnostic types that cross the engine <-> provider boundary."""

from dataclasses import dataclass, field


@dataclass
class MusicQuery:
    """Search parameters derived from a vibe profile, understood by any
    MusicProvider — never provider-specific fields."""

    seed_genres: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    target_energy: float | None = None  # 0.0 (very_low) .. 1.0 (very_high)
    target_valence: float | None = None  # 0.0 (negative) .. 1.0 (positive)
    limit: int = 10


@dataclass
class TrackResult:
    """A real song returned by a MusicProvider."""

    title: str
    artist: str
    provider: str
    external_url: str | None = None
    album_art_url: str | None = None
    preview_url: str | None = None
