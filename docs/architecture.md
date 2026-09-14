# Architecture

## Guiding principle

The core intelligence of this product is **our own trained ML model**, not an
LLM call. The pipeline is designed so the classifier can be swapped —
TF-IDF + Logistic Regression today, a small fine-tuned transformer later —
without touching the API, the recommendation logic, or the frontend.

```
user text ──▶ text preprocessing ──▶ our trained ML model ──▶ VibePrediction
                                                                    │
                                                                    ▼
                                                        RecommendationEngine
                                                     (vibe profile → query params)
                                                                    │
                                                                    ▼
                                                          MusicProvider interface
                                                     (query params → real songs)
                                                          /        |        \
                                                 SpotifyProvider LastFmProvider MockProvider
                                                                    │
                                                                    ▼
                                                              FastAPI (apps/api)
                                                                    │
                                                                    ▼
                                                             Next.js UI (apps/web)
```

## Components and responsibilities

### `apps/web` — Next.js frontend
- Collects user input (text, optional photo, optional preferences).
- Calls the FastAPI backend and renders the vibe profile + recommendations.
- No business logic: it never talks to the ML model, the recommendation
  engine, or a music provider directly.

### `apps/api` — FastAPI backend
- HTTP boundary and orchestration layer only.
- Wires together `vibe_ml` (classification) and `recommendation_engine`
  (query building + provider fan-out).
- Owns persistence (SQLite now, Postgres-compatible later) — e.g. storing
  past vibe queries and their results.
- Does **not** contain model training code or provider-specific API logic.

### `ml/` — `vibe_ml` package (data science / ML)
- Everything about turning raw text into a `VibePrediction`: data
  collection/cleaning, feature engineering, model training, evaluation,
  versioned artifacts, and a stable `predict_vibe(text) -> VibePrediction`
  inference interface.
- Installed as a local editable dependency of `apps/api`. It has no
  knowledge of HTTP, recommendations, or music providers.
- See [ml-plan.md](./ml-plan.md).

### `recommendation/` — `recommendation_engine` package
- Pure translation logic: `VibePrediction -> MusicQuery`.
- Defines the `MusicProvider` abstract interface and a `MockMusicProvider`
  for development/tests. Real providers (Spotify, Last.fm, ...) plug in
  later without changing the engine or the API.
- Has no knowledge of the ML model internals or the HTTP layer.
- See [recommendation-system.md](./recommendation-system.md).

### `packages/shared` — cross-language contract
- JSON Schema definitions for the shapes that cross the frontend/backend
  boundary (`VibeProfile`, `Track`, ...), plus hand-maintained TypeScript
  types generated to match. Keeps `apps/web` and `apps/api` from drifting
  apart without adding a heavyweight schema-generation pipeline yet.

### Why `recommendation/` is its own package, not part of `apps/api`

The product brief calls out five distinct responsibilities: frontend,
backend, ML, recommendation engine, and external providers. Nesting the
recommendation engine inside `apps/api` would blur the line between "HTTP
serving" and "vibe → query business logic." Keeping it a separate,
independently testable package makes the separation the brief asks for
explicit in the directory structure, not just in prose.

## Data flow for one request

1. `POST /vibe` on `apps/api` receives `{ text, photo?, preferences? }`.
2. `apps/api` calls `vibe_ml.predict_vibe(text)` → `VibePrediction`
   (`mood`, `energy`, `valence`, `social_energy`, `vibe_tags`, `confidence`
   — note there's no `context` here, see below).
2b. `apps/api` derives `context` (morning/afternoon/evening/night) from
    the request's own timestamp, not from the model — text essentially
    never states time of day. See `docs/ml-plan.md` and
    `context_from_time` in `apps/api/app/services/vibe_service.py`.
3. `apps/api` calls `recommendation_engine.RecommendationEngine.recommend(prediction, preferences)`.
4. The engine builds a `MusicQuery` and calls the configured `MusicProvider`.
5. The provider returns a list of `TrackResult`s (real songs).
6. `apps/api` persists the query + results, and returns a structured
   response to `apps/web`.
7. `apps/web` renders the vibe summary and the track list.

## Non-goals (for now)

- No authentication.
- No Docker (added once there's something worth containerizing).
- No committed dataset or trained model artifacts — `ml/data` and
  `ml/models` are gitignored except for their `README.md`s.
