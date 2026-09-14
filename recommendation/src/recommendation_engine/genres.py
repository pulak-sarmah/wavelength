"""Rule-based lookup tables: vibe dimensions -> music search parameters.

Recommendation-domain knowledge (genre taxonomy), not ML/vibe-classification
knowledge — hence living here rather than in vibe_ml.labels. Same spirit as
vibe_ml.labels.MOOD_TO_DERIVED: explainable, hand-tuned, and easy to revise
once real provider results are seen. Genre strings are lowercase/hyphenated
(Spotify-style seed genres) since that's the most common shape, but nothing
here is provider-specific.
"""

MOOD_TO_GENRES = {
    "happy": ["pop", "dance", "funk"],
    "sad": ["acoustic", "singer-songwriter", "sad"],
    "calm": ["ambient", "chill", "acoustic"],
    "anxious": ["ambient", "instrumental", "lo-fi"],
    "angry": ["metal", "punk", "hard-rock"],
    "excited": ["edm", "dance", "pop"],
    "romantic": ["r-n-b", "soul", "romance"],
    "nostalgic": ["classic-rock", "oldies", "folk"],
    "neutral": ["indie", "chill", "pop"],
}

ENERGY_TO_TARGET = {
    "very_low": 0.1,
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "very_high": 0.9,
}

VALENCE_TO_TARGET = {
    "negative": 0.2,
    "neutral": 0.5,
    "positive": 0.8,
}
