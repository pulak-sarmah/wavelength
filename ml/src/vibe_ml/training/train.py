"""Train the TF-IDF + Logistic Regression baseline mood classifier.

Usage:
    python -m vibe_ml.training.train [--data-dir ml/data/processed] [--out ml/models/v0]

Reads train.csv (from vibe_ml.data.goemotions), fits the baseline, and
writes a versioned artifact directory: vectorizer.joblib,
mood_classifier.joblib, and metadata.json. Also (re)points ml/models/latest
at it.
"""

import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import sklearn

from vibe_ml.models.baseline import BaselineVibeClassifier

ML_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = ML_ROOT / "data" / "processed"
DEFAULT_OUT_DIR = ML_ROOT / "models" / "v0"
LATEST_LINK = ML_ROOT / "models" / "latest"


def train(data_dir: Path, out_dir: Path) -> BaselineVibeClassifier:
    train_df = pd.read_csv(data_dir / "train.csv")

    model = BaselineVibeClassifier().fit(train_df["text"].tolist(), train_df["mood"].tolist())
    model.save(out_dir)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "tfidf_logistic_regression_baseline",
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
        "train_rows": len(train_df),
        "train_class_counts": train_df["mood"].value_counts().to_dict(),
        "classes": sorted(train_df["mood"].unique().tolist()),
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    if LATEST_LINK.exists() or LATEST_LINK.is_symlink():
        LATEST_LINK.unlink()
    LATEST_LINK.symlink_to(out_dir.name)

    print(f"Trained on {len(train_df)} rows, classes: {metadata['classes']}")
    print(f"Saved to {out_dir} ({LATEST_LINK} -> {out_dir.name})")
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    train(args.data_dir, args.out)


if __name__ == "__main__":
    main()
