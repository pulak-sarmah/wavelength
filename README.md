# Wavelength

A personal AI web app that reads how you're feeling from natural language
(and optionally a photo + preferences), turns it into a structured **vibe
profile**, and recommends real songs that fit — presented as a polished
personal product, not an ML demo.

> Entertainment/personalization, not a mental-health tool. No medical or
> psychological claims are made anywhere in this product.

## Why this project exists

This is primarily an **AI/ML learning project**. The interesting part isn't
"call an LLM and show the result" — it's building and owning the full
lifecycle of a small, real classifier:

```
user text ──▶ preprocessing ──▶ our trained ML model ──▶ vibe profile
                                                              │
                                                              ▼
                                                   recommendation engine
                                                              │
                                                              ▼
                                                     music provider (real API)
                                                              │
                                                              ▼
                                                       FastAPI ──▶ Next.js UI
```

The classifier starts as a lightweight, CPU-friendly baseline (TF-IDF +
Logistic Regression) trained locally, then moves to a small fine-tuned
transformer via Hugging Face `transformers` on PyTorch/MPS (Apple Silicon
Metal acceleration) — without changing anything downstream, because
everything downstream only depends on a stable `predict_vibe(text)`
interface. All training/experimentation for `ml/` happens in Jupyter Lab
inside the existing `ml` miniconda environment (PyTorch with Metal support
already installed there).

## Repository layout

```
wavelength/
├── apps/
│   ├── web/                  Next.js + TypeScript + Tailwind frontend
│   └── api/                  FastAPI backend (HTTP + orchestration + DB)
│
├── ml/                       vibe_ml — data, training, evaluation, inference
│   ├── data/{raw,processed}
│   ├── notebooks/
│   ├── src/vibe_ml/{data,features,models,training,evaluation,inference}
│   ├── models/                versioned trained artifacts (gitignored)
│   └── tests/
│
├── recommendation/           recommendation_engine — vibe → query → provider
│   └── src/recommendation_engine/providers/   MusicProvider + implementations
│
├── packages/
│   └── shared/                cross-language contract (JSON Schema + TS types)
│
├── docs/                      architecture.md, ml-plan.md, recommendation-system.md
├── scripts/                    dev/data utility scripts
├── .env.example
└── package.json                npm workspaces root (web + shared only)
```

See [docs/architecture.md](./docs/architecture.md) for the full component
breakdown and why the layout is shaped this way.

## Status

Scaffolding only. No model is trained, no music provider is wired up, no UI
is built beyond placeholders. See the roadmap below for build order.

## Development roadmap

Built incrementally, one stage at a time, each reviewed before moving on:

1. **Repo scaffolding** *(this stage)* — directory structure, interfaces,
   docs, env examples.
2. **Vibe label taxonomy + dataset plan** — finalize the label set in
   `ml/src/vibe_ml/labels.py` against a real dataset sample.
3. **Data collection & cleaning** — get a workable labeled dataset into
   `ml/data/`.
4. **EDA** — understand label balance and text characteristics.
5. **Baseline model** — TF-IDF + Logistic Regression, trained and evaluated
   in Jupyter Lab (`ml` conda env) as a fast, cheap sanity-check pipeline.
6. **Transformer model** — fine-tune a small Hugging Face transformer on
   PyTorch/MPS in the same environment; compare against the baseline via
   the same evaluation harness before it becomes the model behind
   `predict_vibe(text)`.
7. **Recommendation engine** — vibe profile → `MusicQuery` heuristic, tested
   against the `MockMusicProvider`.
8. **Real music provider** — implement one `MusicProvider` (e.g. Spotify)
   behind the existing interface.
9. **FastAPI wiring** — connect ML + recommendation engine + DB persistence
   behind `POST /vibe`.
10. **Next.js UI** — the full "describe your vibe → see recommendations"
    flow, styled to feel like a real product.
11. **Testing pass** — unit tests across `ml`, `recommendation`, `apps/api`;
    basic frontend checks.
12. **Error analysis & model iteration** — compare baseline vs. transformer
    error patterns, iterate on whichever is behind `predict_vibe`.
13. **Deployment prep** — Docker, once there's a stable end-to-end system
    worth containerizing.

## Tech stack

- **Frontend:** Next.js, TypeScript, React, Tailwind CSS
- **Backend:** Python, FastAPI
- **ML:** scikit-learn (baseline), PyTorch + Hugging Face Transformers, run
  locally on Apple Silicon (MPS) inside a miniconda `ml` environment via
  Jupyter Lab
- **Database:** SQLite for development, designed to migrate to PostgreSQL
- **External music API:** abstracted behind a `MusicProvider` interface —
  no provider is hardcoded into the architecture
