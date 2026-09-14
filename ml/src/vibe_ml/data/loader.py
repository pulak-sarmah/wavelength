"""Load and clean raw vibe-labeled text data.

Placeholder — implement once a raw dataset exists in ml/data/raw/.
"""

from pathlib import Path

import pandas as pd


def load_raw_dataset(path: Path) -> pd.DataFrame:
    """Load a raw labeled dataset from ml/data/raw/ into a DataFrame."""
    raise NotImplementedError("No raw dataset defined yet. See ml/data/README.md.")


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize text, drop duplicates/nulls, and validate label values."""
    raise NotImplementedError("Cleaning rules not defined yet.")
