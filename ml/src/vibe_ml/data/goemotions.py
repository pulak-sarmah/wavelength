"""Load GoEmotions and map it onto our mood taxonomy.

GoEmotions (Demszky et al., 2020) is ~58k Reddit comments labeled with 28
fine-grained emotions. We keep only single-label rows (multi-label rows are
genuinely ambiguous for a single mood target) and map GoEmotions' labels
onto our 9-way mood taxonomy via `vibe_ml.labels.GOEMOTIONS_TO_MOOD`. Rows
whose label has no mapping (e.g. confusion, curiosity, realization,
surprise) are dropped rather than force-fit.

Usage:
    python -m vibe_ml.data.goemotions
"""

from pathlib import Path

import pandas as pd
from datasets import load_dataset

from vibe_ml.labels import GOEMOTIONS_TO_MOOD

PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"

# GoEmotions' own train/validation/test split; we keep it rather than
# re-splitting so results stay comparable to published baselines.
_SPLIT_NAMES = {"train": "train", "val": "validation", "test": "test"}


def _map_split(dataset, label_names: list[str]) -> pd.DataFrame:
    rows = []
    for example in dataset:
        if len(example["labels"]) != 1:
            continue  # drop multi-label / unlabeled rows
        label_name = label_names[example["labels"][0]]
        mood = GOEMOTIONS_TO_MOOD.get(label_name)
        if mood is None:
            continue  # drop labels with no clean mood mapping
        rows.append({"text": example["text"], "mood": mood, "source_label": label_name})
    return pd.DataFrame(rows)


def load_and_map_goemotions() -> dict[str, pd.DataFrame]:
    """Load GoEmotions and return {split_name: DataFrame(text, mood, source_label)}."""
    dataset = load_dataset("google-research-datasets/go_emotions", "simplified")
    label_names = dataset["train"].features["labels"].feature.names
    return {split: _map_split(dataset[hf_split], label_names) for split, hf_split in _SPLIT_NAMES.items()}


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    splits = load_and_map_goemotions()
    for split, df in splits.items():
        out_path = PROCESSED_DIR / f"{split}.csv"
        df.to_csv(out_path, index=False)
        print(f"{split}: {len(df)} rows -> {out_path}")
        print(df["mood"].value_counts().to_string())
        print()


if __name__ == "__main__":
    main()
