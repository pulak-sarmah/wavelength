"""Baseline model: TF-IDF features + a single multiclass Logistic Regression
over the mood taxonomy.

Bundles the vectorizer + classifier together so training, evaluation, and
inference all share one save/load path instead of re-implementing it three
times.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

from vibe_ml.features.text_features import build_tfidf_vectorizer


def new_logistic_regression() -> LogisticRegression:
    return LogisticRegression(max_iter=1000, class_weight="balanced")


@dataclass
class BaselineVibeClassifier:
    vectorizer: TfidfVectorizer | None = None
    classifier: LogisticRegression | None = None

    def fit(self, texts: list[str], moods: list[str]) -> "BaselineVibeClassifier":
        self.vectorizer = build_tfidf_vectorizer()
        features = self.vectorizer.fit_transform(texts)
        self.classifier = new_logistic_regression()
        self.classifier.fit(features, moods)
        return self

    def predict(self, text: str) -> tuple[str, float]:
        """Return (predicted_mood, confidence)."""
        features = self.vectorizer.transform([text])
        proba = self.classifier.predict_proba(features)[0]
        best_idx = proba.argmax()
        return str(self.classifier.classes_[best_idx]), float(proba[best_idx])

    def predict_batch(self, texts: list[str]) -> list[str]:
        return [mood for mood, _ in self.predict_batch_with_confidence(texts)]

    def predict_batch_with_confidence(self, texts: list[str]) -> list[tuple[str, float]]:
        features = self.vectorizer.transform(texts)
        proba = self.classifier.predict_proba(features)
        best_idx = proba.argmax(axis=1)
        return [
            (str(self.classifier.classes_[idx]), float(proba[row, idx]))
            for row, idx in enumerate(best_idx)
        ]

    def save(self, model_dir: Path) -> None:
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, model_dir / "vectorizer.joblib")
        joblib.dump(self.classifier, model_dir / "mood_classifier.joblib")

    @classmethod
    def load(cls, model_dir: Path) -> "BaselineVibeClassifier":
        vectorizer = joblib.load(model_dir / "vectorizer.joblib")
        classifier = joblib.load(model_dir / "mood_classifier.joblib")
        return cls(vectorizer=vectorizer, classifier=classifier)
