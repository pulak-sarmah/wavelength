"""Evaluate a trained baseline model against the held-out test split.

Usage:
    python -m vibe_ml.evaluation.evaluate [--model-dir ml/models/latest] [--data-dir ml/data/processed]

Writes metrics.json (per-class precision/recall/F1 + macro-F1) and a
confusion matrix PNG into the model directory, and prints a summary.
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, classification_report

from vibe_ml.models import load_classifier

ML_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_DIR = ML_ROOT / "models" / "latest"
DEFAULT_DATA_DIR = ML_ROOT / "data" / "processed"


def evaluate_model(model_dir: Path, data_dir: Path) -> dict:
    model = load_classifier(model_dir)
    test_df = pd.read_csv(data_dir / "test.csv")

    y_true = test_df["mood"].tolist()
    y_pred = model.predict_batch(test_df["text"].tolist())

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "test_rows": len(test_df),
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
        "accuracy": report["accuracy"],
        "per_class": {
            label: values
            for label, values in report.items()
            if label not in ("accuracy", "macro avg", "weighted avg")
        },
    }
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    labels = sorted(set(y_true) | set(y_pred))
    fig, ax = plt.subplots(figsize=(7, 7))
    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, labels=labels, ax=ax, xticks_rotation=45)
    fig.tight_layout()
    fig.savefig(model_dir / "confusion_matrix.png", dpi=150)
    plt.close(fig)

    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    args = parser.parse_args()

    metrics = evaluate_model(args.model_dir.resolve(), args.data_dir)
    print(f"accuracy: {metrics['accuracy']:.3f}  macro_f1: {metrics['macro_f1']:.3f}  weighted_f1: {metrics['weighted_f1']:.3f}")
    for label, values in sorted(metrics["per_class"].items()):
        print(f"  {label:10s} precision={values['precision']:.2f} recall={values['recall']:.2f} f1={values['f1-score']:.2f} support={values['support']}")


if __name__ == "__main__":
    main()
