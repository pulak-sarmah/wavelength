"""Model loading dispatch.

Every model directory (ml/models/v0, v1, ...) carries a metadata.json with
a `model_type` field. This is the single place that maps that field to the
right classifier class, so callers (evaluate.py, inference/predictor.py)
never need to know or care which kind of model they're holding — both
expose the same `.predict`/`.predict_batch` interface.
"""

import json
from pathlib import Path
from typing import Protocol


class VibeClassifier(Protocol):
    def predict(self, text: str) -> tuple[str, float]: ...
    def predict_batch(self, texts: list[str]) -> list[str]: ...


def load_classifier(model_dir: Path) -> VibeClassifier:
    metadata = json.loads((model_dir / "metadata.json").read_text())
    model_type = metadata["model_type"]

    if model_type == "tfidf_logistic_regression_baseline":
        from vibe_ml.models.baseline import BaselineVibeClassifier

        return BaselineVibeClassifier.load(model_dir)

    if model_type == "distilbert_transformer":
        from vibe_ml.models.transformer import TransformerVibeClassifier

        return TransformerVibeClassifier.load(model_dir)

    raise ValueError(f"Unknown model_type {model_type!r} in {model_dir}")
