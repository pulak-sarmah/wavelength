"""The abstraction every music service plugs into.

Nothing in `engine.py` or `apps/api` should ever import a concrete
provider directly by name — they depend on this interface, and the
concrete provider is chosen by configuration (see MUSIC_PROVIDER in
.env.example).
"""

from abc import ABC, abstractmethod

from recommendation_engine.types import MusicQuery, TrackResult


class MusicProvider(ABC):
    @abstractmethod
    def search(self, query: MusicQuery) -> list[TrackResult]:
        """Search for real songs matching the given query parameters."""
        raise NotImplementedError
