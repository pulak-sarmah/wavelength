# apps/api

FastAPI backend. HTTP boundary and orchestration only — wires together
`vibe_ml` (classification) and `recommendation_engine` (query building +
provider fan-out), and owns persistence. See
[../../docs/architecture.md](../../docs/architecture.md).

## Layout

```
app/
├── main.py               FastAPI app instance
├── core/config.py          Settings (env-driven, pydantic-settings)
├── api/routes/             health.py, vibe.py
├── schemas/                VibeRequest, RecommendationResponse (pydantic)
├── db/                     SQLAlchemy session + models
└── services/               vibe_service.py — orchestrates ML + engine + DB
```

## Setup

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../../ml -e ../../recommendation
uvicorn app.main:app --reload
```

For local dev, these were installed into the existing `ml` conda env
instead (already has `vibe_ml`/`recommendation_engine` importable) — a
standalone venv is the path for an eventual separate/production setup.

## Status

`POST /vibe` works end-to-end: `vibe_ml.predict_vibe` → `RecommendationEngine`
→ a real `MusicProvider` → `RecommendationResponse`, and each request is
persisted to SQLite (`app/db/models.py`'s `VibeQuery`, tables created at
startup in `app/main.py`).

The music provider is chosen by `MUSIC_PROVIDER` (see `.env.example`):
`"jamendo"` (real, open-content tracks — needs `JAMENDO_CLIENT_ID`) or the
default `"mock"`, which is also the automatic fallback if no Jamendo
client ID is configured — the app never hard-fails for a missing key.

Tests: `pytest` (`tests/test_health.py`, `tests/test_vibe.py`,
`tests/test_persistence.py`).
