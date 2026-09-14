"""Feature engineering for the baseline model.

First feature set: TF-IDF over cleaned text. Kept as a thin wrapper around
scikit-learn so it can be swapped for embeddings later without touching
training/inference call sites.
"""

from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf_vectorizer(**kwargs) -> TfidfVectorizer:
    """Construct the TF-IDF vectorizer used by the baseline model.

    Placeholder defaults — tune once real data + EDA exist.
    """
    defaults = dict(max_features=20_000, ngram_range=(1, 2), min_df=2)
    defaults.update(kwargs)
    return TfidfVectorizer(**defaults)
