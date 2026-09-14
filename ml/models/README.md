# ml/models

Versioned trained model artifacts. Gitignored — these are build outputs,
not source. Regenerate via `vibe_ml.training.train`.

Expected layout once training exists:

```
ml/models/
├── v0/
│   ├── vectorizer.joblib
│   ├── mood_classifier.joblib
│   ├── energy_classifier.joblib
│   ├── valence_classifier.joblib
│   ├── context_classifier.joblib
│   ├── social_energy_classifier.joblib
│   ├── label_encoders.joblib
│   └── metadata.json        training config, dataset version, metrics
└── latest -> v0             symlink (or copy) the API loads at startup
```

`VIBE_MODEL_PATH` in `.env` points at the directory the API should load
(defaults to `ml/models/latest`).
