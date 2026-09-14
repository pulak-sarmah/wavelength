"""Fine-tune DistilBERT for mood classification.

Uses the same train/val split and the same class-weighted-imbalance
strategy as the baseline (ml/src/vibe_ml/training/train.py) so the two
models' metrics are directly comparable.

Usage:
    python -m vibe_ml.training.train_transformer
    python -m vibe_ml.training.train_transformer --limit 500 --epochs 1   # smoke test
"""

import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import transformers
from datasets import Dataset
from sklearn.utils.class_weight import compute_class_weight
from transformers import Trainer, TrainingArguments

from vibe_ml.models.transformer import MAX_LENGTH, MODEL_NAME, TransformerVibeClassifier, get_device

ML_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = ML_ROOT / "data" / "processed"
DEFAULT_OUT_DIR = ML_ROOT / "models" / "v1"


class WeightedLossTrainer(Trainer):
    """Trainer with per-class weighted cross-entropy, mirroring the
    baseline's class_weight="balanced" so imbalance handling is consistent
    across both models."""

    def __init__(self, *args, class_weights: torch.Tensor, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss = torch.nn.functional.cross_entropy(logits, labels, weight=self.class_weights.to(logits.device))
        return (loss, outputs) if return_outputs else loss


def build_dataset(df: pd.DataFrame, tokenizer, label2id: dict[str, int]) -> Dataset:
    ds = Dataset.from_pandas(df[["text", "mood"]].reset_index(drop=True))

    def tokenize(batch):
        encoded = tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH, padding="max_length")
        encoded["labels"] = [label2id[m] for m in batch["mood"]]
        return encoded

    return ds.map(tokenize, batched=True, remove_columns=["text", "mood"])


def train(data_dir: Path, out_dir: Path, epochs: int, limit: int | None) -> None:
    train_df = pd.read_csv(data_dir / "train.csv")
    val_df = pd.read_csv(data_dir / "val.csv")
    if limit:
        train_df = train_df.sample(min(limit, len(train_df)), random_state=0).reset_index(drop=True)
        val_df = val_df.sample(min(max(limit // 5, 10), len(val_df)), random_state=0).reset_index(drop=True)

    classes = sorted(train_df["mood"].unique())
    label2id = {label: i for i, label in enumerate(classes)}

    classifier = TransformerVibeClassifier.from_pretrained_base(label2id)
    tokenizer = classifier.tokenizer

    train_ds = build_dataset(train_df, tokenizer, label2id)
    val_ds = build_dataset(val_df, tokenizer, label2id)

    class_weights = compute_class_weight(
        class_weight="balanced", classes=np.array(classes), y=train_df["mood"].to_numpy()
    )
    class_weights_t = torch.tensor(class_weights, dtype=torch.float32)

    training_args = TrainingArguments(
        output_dir=str(out_dir / "_checkpoints"),
        num_train_epochs=epochs,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=50,
        report_to=[],
    )

    trainer = WeightedLossTrainer(
        model=classifier.model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        class_weights=class_weights_t,
    )
    trainer.train()

    classifier.model.eval()
    classifier.save(out_dir)

    metadata = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "distilbert_transformer",
        "base_model": MODEL_NAME,
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_version": platform.python_version(),
        "device": str(get_device()),
        "epochs": epochs,
        "max_length": MAX_LENGTH,
        "train_rows": len(train_df),
        "train_class_counts": train_df["mood"].value_counts().to_dict(),
        "classes": classes,
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Saved to {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--limit", type=int, default=None, help="Cap train rows (for a fast smoke test)")
    args = parser.parse_args()
    train(args.data_dir, args.out, args.epochs, args.limit)


if __name__ == "__main__":
    main()
