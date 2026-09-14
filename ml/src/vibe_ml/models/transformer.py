"""Transformer model: fine-tuned DistilBERT for mood classification.

Mirrors BaselineVibeClassifier's interface (predict/predict_batch/save/load)
so evaluate.py and predictor.py can treat either model interchangeably —
see vibe_ml.models.load_classifier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 64
_BATCH_SIZE = 32


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@dataclass
class TransformerVibeClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer
    id2label: dict[int, str]
    device: torch.device = field(default_factory=get_device)

    def __post_init__(self) -> None:
        self.model.to(self.device)
        self.model.eval()

    @classmethod
    def from_pretrained_base(cls, label2id: dict[str, int]) -> "TransformerVibeClassifier":
        """A fresh model initialized from the pretrained base, ready for fine-tuning."""
        id2label = {i: label for label, i in label2id.items()}
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, num_labels=len(label2id), id2label=id2label, label2id=label2id
        )
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        return cls(model=model, tokenizer=tokenizer, id2label=id2label)

    def _predict_proba(self, texts: list[str]) -> torch.Tensor:
        inputs = self.tokenizer(
            texts, padding=True, truncation=True, max_length=MAX_LENGTH, return_tensors="pt"
        ).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        return F.softmax(logits, dim=-1)

    def predict(self, text: str) -> tuple[str, float]:
        proba = self._predict_proba([text])[0]
        idx = int(proba.argmax())
        return self.id2label[idx], float(proba[idx])

    def predict_batch(self, texts: list[str]) -> list[str]:
        return [mood for mood, _ in self.predict_batch_with_confidence(texts)]

    def predict_batch_with_confidence(self, texts: list[str]) -> list[tuple[str, float]]:
        results: list[tuple[str, float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            chunk = texts[start : start + _BATCH_SIZE]
            proba = self._predict_proba(chunk)
            values, idxs = proba.max(dim=-1)
            results.extend(
                (self.id2label[idx], float(val)) for idx, val in zip(idxs.tolist(), values.tolist())
            )
        return results

    def save(self, model_dir: Path) -> None:
        model_dir.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(model_dir)
        self.tokenizer.save_pretrained(model_dir)

    @classmethod
    def load(cls, model_dir: Path) -> "TransformerVibeClassifier":
        model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        tokenizer = AutoTokenizer.from_pretrained(model_dir)
        id2label = {int(i): label for i, label in model.config.id2label.items()}
        return cls(model=model, tokenizer=tokenizer, id2label=id2label)
