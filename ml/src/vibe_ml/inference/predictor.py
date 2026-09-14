"""The stable inference interface every downstream consumer depends on.

apps/api imports only `predict_vibe` and `VibePrediction` from this
package. The internals (baseline TF-IDF+LogReg today, a small transformer
later) can change freely as long as this interface holds.

Note: `context` (time of day) is deliberately not part of `VibePrediction`
— it's assembled by the caller from the request timestamp, not predicted
from text. See docs/ml-plan.md and apps/api/app/services/vibe_service.py.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from vibe_ml.labels import MOOD_TO_DERIVED
from vibe_ml.models import VibeClassifier, load_classifier

_ML_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_MODEL_PATH = _ML_ROOT / "models" / "latest"

_model: VibeClassifier | None = None


@dataclass
class VibePrediction:
    mood: str
    energy: str
    valence: str
    social_energy: str
    vibe_tags: list[str] = field(default_factory=list)
    confidence: float = 0.0


def _model_path() -> Path:
    configured = os.environ.get("VIBE_MODEL_PATH")
    return Path(configured).resolve() if configured else _DEFAULT_MODEL_PATH


def _get_model() -> VibeClassifier:
    global _model
    if _model is None:
        model_path = _model_path()
        if not model_path.exists():
            raise RuntimeError(
                f"No trained model found at {model_path}. "
                "Run `python -m vibe_ml.training.train` first."
            )
        _model = load_classifier(model_path)
    return _model


def predict_vibe(text: str) -> VibePrediction:
    """Classify raw user text into a structured vibe profile."""
    model = _get_model()
    mood, confidence = model.predict(text)
    derived = MOOD_TO_DERIVED[mood]
    return VibePrediction(
        mood=mood,
        energy=derived["energy"],
        valence=derived["valence"],
        social_energy=derived["social_energy"],
        vibe_tags=list(derived["vibe_tags"]),
        confidence=confidence,
    )
