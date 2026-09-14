# Recommendation System

## Separation of concerns

The ML model never picks a song. It only produces a `VibePrediction`. Two
more layers turn that into real recommendations:

```
VibePrediction
      │
      ▼
RecommendationEngine.recommend(prediction, preferences)
      │   builds a provider-agnostic MusicQuery
      ▼
MusicProvider.search(query) -> list[TrackResult]
      │
      ▼
JamendoProvider / MockMusicProvider
```

This keeps each layer independently testable:
- The engine can be unit-tested with a fake provider and fixed
  `VibePrediction`s — no network calls, no ML model.
- A provider can be tested against its own API contract in isolation.
- Swapping music services later means writing one new `MusicProvider`
  implementation; nothing else changes.

## `MusicQuery` (engine → provider contract)

Provider-agnostic search parameters derived from the vibe profile —
things like target energy/valence ranges, mood-derived seed genres or
keywords, and a result limit. Defined in
`recommendation/src/recommendation_engine/types.py`.

## `MusicProvider` interface

```python
class MusicProvider(ABC):
    def search(self, query: MusicQuery) -> list[TrackResult]: ...
```

Implementations translate a `MusicQuery` into that service's actual API
calls and map results back into `TrackResult`. None of this logic — auth,
rate limits, response parsing — leaks into the engine or the API layer.

## Mapping vibe → query (heuristic, not ML)

**Done.** `RecommendationEngine.build_query`
(`recommendation/src/recommendation_engine/engine.py`) is a simple,
explainable, rule-based mapping — deliberately not a learned model, same
reasoning as `vibe_ml.labels.MOOD_TO_DERIVED`:

- `mood → seed_genres`: a fixed lookup table,
  `recommendation_engine.genres.MOOD_TO_GENRES` (e.g. `sad` → `["acoustic",
  "singer-songwriter", "sad"]`, `angry` → `["metal", "punk", "hard-rock"]`).
  A user-supplied `preferences["genres"]` fully overrides this.
- `vibe_tags → keywords`: passed straight through. (Not every provider can
  use this — see Jamendo's limitation below.)
- `energy`/`valence → target_energy`/`target_valence`: mapped to 0–1
  floats (`ENERGY_TO_TARGET`, `VALENCE_TO_TARGET` in the same module) —
  the shape most streaming APIs' recommendation endpoints expect.
- `preferences["limit"]` overrides the default result count (10).

`prediction.confidence` isn't used yet (e.g. to broaden the query when the
model is unsure) — a plausible future refinement, skipped for v1 to keep
the first version simple.

## Current status

The engine is fully implemented and unit-tested
(`recommendation/tests/test_engine.py`). Two providers exist:
`MockMusicProvider` (static placeholder tracks, always available, no
credentials) and `JamendoProvider` (`recommendation/src/recommendation_engine/providers/jamendo_provider.py`)
— real, Creative Commons-licensed, streamable tracks from
[Jamendo](https://www.jamendo.com), chosen for being genuinely open
(free `client_id`, no OAuth) and for returning a direct playable audio URL
in the search response itself. `apps/api` picks between them via
`MUSIC_PROVIDER` (`.env.example`), falling back to mock whenever
`JAMENDO_CLIENT_ID` isn't set rather than hard-failing.

**Verified against the real API, not just mocked tests** — and two things
turned out to work differently than the obvious first implementation
assumed (see the module docstring in `jamendo_provider.py` for the full
detail):

- **`tags` is a single-genre filter, not an OR list.** Sending
  `query.seed_genres` as one comma-joined string requires a track to
  match *all* of them at once, which is so narrow it reliably returns
  nothing. `JamendoProvider` instead tries each genre in `seed_genres` as
  its own request, falling through to the next on an empty result, then
  to no genre filter at all as a last resort.
- **Jamendo's `search` does literal text matching** against track/artist
  names — it's not a semantic filter, so `query.keywords` (mood words
  like "calm", "energetic") were never a meaningful fit for it and
  aren't sent. Only `seed_genres` maps to a real Jamendo parameter.
  `target_energy`/`target_valence` still have no equivalent at all (no
  audio-features endpoint like Spotify's) — a provider with richer search
  (or a post-filter step) could use them later without changing the
  engine.
- **The API itself is flaky at the backend level**: the exact same
  single-tag request, repeated back to back with nothing changed, returns
  a full page of results about half the time and zero the other half.
  `JamendoProvider` retries each genre a couple of times before moving on
  — without that, the recommendation would intermittently come back empty
  for no reason a user could understand.
