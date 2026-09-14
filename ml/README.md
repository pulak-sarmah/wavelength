# vibe_ml

The data science / ML component of Wavelength. Owns the full
lifecycle from raw text to a trained classifier: data, features, training,
evaluation, versioned artifacts, and inference.

See [../docs/ml-plan.md](../docs/ml-plan.md) for the full plan and label
taxonomy, and [../docs/architecture.md](../docs/architecture.md) for how
this package fits into the rest of the system.

## The one interface everything else depends on

```python
from vibe_ml import predict_vibe

prediction = predict_vibe("I've had a terrible day, I just want to lie down and forget everything.")
# VibePrediction(mood="sad", energy="low", valence="negative", ...)
```

`apps/api` depends on this package for that function and nothing else —
not on training code, not on raw data. That's what lets the model evolve
(baseline → transformer) without touching serving code.

## Layout

```
ml/
├── data/
│   ├── raw/            untouched source data (gitignored)
│   └── processed/      cleaned/feature-ready data (gitignored)
├── notebooks/           EDA and experimentation
├── src/vibe_ml/
│   ├── labels.py         label taxonomy (single source of truth)
│   ├── data/              loading & cleaning
│   ├── features/          feature engineering (TF-IDF, etc.)
│   ├── models/            model definitions (baseline + future)
│   ├── training/          training entrypoints
│   ├── evaluation/        metrics, confusion matrices, error analysis
│   └── inference/         predict_vibe(text) -> VibePrediction
├── models/               versioned trained artifacts (gitignored)
└── tests/
```

## Setup

Development happens inside the existing miniconda `ml` environment
(PyTorch with Metal/MPS support already installed there), driven from
Jupyter Lab for EDA/experimentation and plain scripts for anything meant
to be reproducible/versioned.

```bash
conda activate ml
pip install -r requirements.txt
pip install -e .          # installs vibe_ml itself, editable
jupyter lab                # open ml/notebooks/
```

If your conda environment isn't literally named `ml`, swap the name above.

## Status

Interfaces and structure only — no data collected, no model trained yet.
`predict_vibe` currently raises `NotImplementedError`.
