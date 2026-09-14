# ML Plan

## Problem framing

Given free-text describing how someone feels, predict a structured vibe
profile: `mood`, `energy`, `valence`, `context`, `social_energy`, plus
free-form `vibe_tags` and a `confidence` score. This is not open-ended
generation, and not a diagnostic or clinical tool.

Only `mood` is actually learned from text. There's no public dataset that
labels energy, valence, social_energy, or time-of-day context for
arbitrary text, so:

- **`mood`** — the real ML target. A single multiclass classifier
  (`ml/src/vibe_ml/models/baseline.py`), trained on GoEmotions mapped onto
  our taxonomy (see below).
- **`energy`, `valence`, `social_energy`, `vibe_tags`** — derived from the
  predicted mood via a fixed, hand-written lookup table,
  `vibe_ml.labels.MOOD_TO_DERIVED`. Explainable and honest about having no
  ground truth for these dimensions, rather than pretending to learn them
  from nothing. Revisit with real modeling (e.g. an arousal/valence
  lexicon) if this proves too coarse once we see real outputs.
- **`context`** — not part of `VibePrediction` at all. Read off the
  request's own timestamp by `apps/api` (`context_from_time` in
  `apps/api/app/services/vibe_service.py`), since text essentially never
  states time of day.

## Label taxonomy

| Dimension       | Values |
|-----------------|--------|
| `mood`          | happy, sad, calm, anxious, angry, excited, romantic, nostalgic, neutral |
| `energy`        | very_low, low, medium, high, very_high |
| `valence`       | negative, neutral, positive |
| `context`       | morning, afternoon, evening, night, unknown |
| `social_energy` | low, medium, high |

Defined in `ml/src/vibe_ml/labels.py` as the single source of truth
(`MOOD_LABELS`, `GOEMOTIONS_TO_MOOD`, `MOOD_TO_DERIVED`).

`nostalgic` is defined but currently has **zero training examples** —
GoEmotions has no analogue for it. The baseline classifier is trained on
the 8 moods that do have data; `nostalgic` stays as a documented gap, not
a working class. `calm` has very thin support (88 rows) and is expected to
have weak recall. See `ml/data/README.md` for exact counts.

## Hardware & environment

Apple M1 (MPS, no CUDA). All choices below must train in minutes-to-an-hour
on a laptop, not hours-to-days on a GPU cluster.

Local dev already has what's needed: a miniconda `ml` environment with
PyTorch built for Metal (MPS) acceleration, and Jupyter Lab. All EDA,
training, and evaluation happens there — `ml/notebooks/` for exploration,
`ml/src/vibe_ml/` for anything promoted to real, reusable code. See
`ml/README.md` for the exact setup commands.

## Planned lifecycle

1. **Dataset** — [GoEmotions](https://huggingface.co/datasets/google-research-datasets/go_emotions)
   (`simplified`), ~43k/5.4k/5.4k train/val/test Reddit comments, 28
   fine-grained emotions, loaded via Hugging Face `datasets` and mapped
   onto our mood taxonomy by `ml/src/vibe_ml/data/goemotions.py`. Not
   vendored into git — reproducible via `python -m vibe_ml.data.goemotions`.
   Documented in `ml/data/README.md`.
2. **Data cleaning** — multi-label rows and rows with no clean mood mapping
   (`confusion`, `curiosity`, `realization`, `surprise`) are dropped rather
   than force-fit; handled in the mapping step above.
3. **EDA** — `ml/notebooks/01_eda.ipynb`: label distribution, text length,
   sample rows per mood, explicit call-out of the `nostalgic`/`calm` gaps.
4. **Feature engineering** — TF-IDF over cleaned text as the first feature
   set (`ml/src/vibe_ml/features/`).
5. **Baseline model** — TF-IDF + a single multiclass Logistic Regression
   over the 8 supported moods (`ml/src/vibe_ml/models/baseline.py`). Trains
   in seconds on CPU; gives us an evaluable end-to-end pipeline and a
   metrics baseline fast, before investing in a heavier model. **Done** —
   `ml/models/v0/`: accuracy 0.62, macro-F1 0.50 on the test split (weak on
   `calm`/`excited`, the smallest classes; strongest on `happy`/`neutral`).
6. **Baseline training + evaluation** — `ml/src/vibe_ml/training/train.py`
   and `ml/src/vibe_ml/evaluation/evaluate.py`; per-class precision/recall/F1
   + confusion matrix written to `ml/models/v0/metrics.json` and
   `confusion_matrix.png`. **Done.**
7. **Transformer model** — fine-tune `distilbert-base-uncased`
   (`ml/src/vibe_ml/training/train_transformer.py`) on the same
   train/val split as the baseline, with the same class-weighted-imbalance
   strategy, on PyTorch/MPS. **Done** — `ml/models/v1/`: 3 epochs, ~50 min
   on M1 MPS. Result: accuracy 0.68, macro-F1 0.585 — a clear improvement
   over the baseline's 0.50 macro-F1, and specifically better on exactly
   the classes the baseline struggled with (`excited` F1 0.35→0.41,
   `calm` F1 0.15→0.30, `sad` F1 0.50→0.61). `neutral` is still a
   confusable sink (see `ml/models/v1/confusion_matrix.png`), but less so
   than before. `ml/models/latest` now points at `v1`.
8. **Model evaluation & selection** — compare baseline vs. transformer on
   the same metrics (`ml/models/{v0,v1}/metrics.json`); whichever wins (or
   a documented reason to keep both) becomes the model behind
   `predict_vibe` — both `BaselineVibeClassifier` and
   `TransformerVibeClassifier` implement the same `.predict`/`.predict_batch`
   interface (`vibe_ml.models.load_classifier` dispatches on each model
   directory's `metadata.json`), so switching `ml/models/latest` is the
   only thing that changes.
9. **Error analysis** — **Done**, see below. `ml/notebooks/02_error_analysis.ipynb`.
10. **Model versioning** — artifacts written to `ml/models/<version>/`
    (vectorizer+classifiers, or the fine-tuned transformer weights, plus
    label encoders and a `metadata.json` with metrics and training config).
    `ml/models/latest` points at the version the API loads.
11. **Model inference** — `predict_vibe(text) -> VibePrediction`
    (`ml/src/vibe_ml/inference/predictor.py`), the only surface `apps/api`
    depends on — agnostic to whether the loaded artifact is the baseline
    or the transformer.

## Error analysis findings (v1)

From `ml/notebooks/02_error_analysis.ipynb`, run against the full test
split (4141 rows, 1310 errors at v1's 68.4% accuracy).

**Calibration is reasonable but not sharp.** Mean confidence on correct
predictions is 0.838 vs. 0.701 on errors — a real gap, but with enough
overlap that confidence alone can't reliably flag a wrong prediction.
237 of the 1310 errors (18%) are "confidently wrong" (>0.9 confidence),
and reading a sample of those surfaced two distinct, more useful patterns
than "the model is bad":

1. **A meaningful chunk of "errors" are actually noisy or coarse ground
   truth, not model mistakes.** E.g. a comment that says *"...I was too
   scared to see something gruesome"* is GoEmotions-labeled `neutral`
   (→ our `neutral`); the model said `anxious` — which is arguably the
   *better* answer. Same pattern for *"I'm really excited for [NAME]..."*
   (labeled `optimism` → mapped to `happy`; predicted `excited`, which is
   the literal word used in the text). This means the baseline/v1 macro-F1
   numbers likely **understate** real quality somewhat — some fraction of
   "errors" are the model disagreeing with an imperfect label, not with
   reality. It also flags specific entries in `GOEMOTIONS_TO_MOOD`
   (`labels.py`) worth revisiting, e.g. `optimism → happy` swallows cases
   that read as `excited`.
2. **Lexical fixation on a single emotionally-loaded word**, independent
   of overall sentence sentiment. *"Noooo no more NEXTs anymore! They are
   obviously just a kid who is excited to discover music. Give them a
   break!"* (true `angry`, source `disapproval`) → predicted `excited`,
   apparently keying on the literal word "excited" later in the sentence.
   Similarly, `sad` texts containing "worry" or "sorry" (*"Yes of mine
   worry, no one liked mine either"*, true `sad` → predicted `anxious`)
   get pulled toward `anxious`. This is a genuine model limitation —
   short-context models latching onto individual charged words rather
   than integrating the whole sentence — worth watching if more data or a
   bigger model is tried later.

**Confusion is dominated by `neutral`, in both directions** — consistent
with the confusion matrix, but the raw counts make it concrete:
`neutral→angry` (245), `neutral→happy` (154), `happy→neutral` (122),
`angry→neutral` (88). GoEmotions' `neutral` is a large, heterogeneous
catch-all (everyday Reddit comments with only mild tone), so this is
expected rather than surprising.

**Sarcasm is a real, if small, gap.** *"Not at all. It's great of course
for financial [...]"* — sarcastic, GoEmotions-labeled `sadness` (→ `sad`),
predicted `anxious`. TF-IDF-era and transformer-era models both lack any
mechanism for detecting irony from a single short comment; this is a
known hard problem, not something to chase for this project's scope.

**Practical takeaway:** the model is in better shape than the raw
macro-F1 suggests once label noise is accounted for, but has a real,
specific weakness (single-word lexical fixation) that's worth keeping in
mind if `predict_vibe` output looks wrong on a real user's input — check
whether an emotionally loaded word is present that doesn't match the
overall tone.

## Explicit non-goals

- No training an LLM from scratch.
- No large transformer models or datasets that don't fit comfortably in
  M1 memory/time budgets.
- No CUDA-only tooling.
- No mental-health or clinical claims — this is personalization/entertainment,
  and the label taxonomy and copy should stay in that register.
