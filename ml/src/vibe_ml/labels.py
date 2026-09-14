"""Vibe label taxonomy — the single source of truth for what the model predicts.

Kept deliberately small and fixed for the baseline. Expect to revise these
after EDA on the actual dataset (see docs/ml-plan.md).
"""

MOOD_LABELS = [
    "happy",
    "sad",
    "calm",
    "anxious",
    "angry",
    "excited",
    "romantic",
    "nostalgic",
    "neutral",
]

ENERGY_LABELS = ["very_low", "low", "medium", "high", "very_high"]

VALENCE_LABELS = ["negative", "neutral", "positive"]

CONTEXT_LABELS = ["morning", "afternoon", "evening", "night", "unknown"]

SOCIAL_ENERGY_LABELS = ["low", "medium", "high"]

# GoEmotions (28 fine-grained labels) -> our 9-mood taxonomy.
#
# Not exhaustive by design: labels with no clean single-mood correspondence
# (confusion, curiosity, realization, surprise — genuinely ambiguous valence)
# are left unmapped and dropped during dataset prep rather than force-fit.
#
# "nostalgic" has no GoEmotions analogue at all, so it currently gets zero
# training rows from this dataset — see ml/data/README.md. It stays in
# MOOD_LABELS/MOOD_TO_DERIVED as a documented gap, not a working class, until
# a dataset or hand-labeled seed set actually supports it.
GOEMOTIONS_TO_MOOD = {
    "admiration": "happy",
    "amusement": "happy",
    "anger": "angry",
    "annoyance": "angry",
    "approval": "happy",
    "caring": "romantic",
    "desire": "romantic",
    "disappointment": "sad",
    "disapproval": "angry",
    "disgust": "angry",
    "embarrassment": "anxious",
    "excitement": "excited",
    "fear": "anxious",
    "gratitude": "happy",
    "grief": "sad",
    "joy": "happy",
    "love": "romantic",
    "nervousness": "anxious",
    "optimism": "happy",
    "pride": "happy",
    "relief": "calm",
    "remorse": "sad",
    "sadness": "sad",
    "neutral": "neutral",
}

# Rule-based lookup for the dimensions we don't have (and likely never will
# have, from generic text alone) labeled training data for. Keyed on the
# predicted mood; deliberately simple and hand-tuned rather than learned.
# See docs/ml-plan.md and docs/recommendation-system.md for the reasoning.
MOOD_TO_DERIVED = {
    "happy": {
        "energy": "high",
        "valence": "positive",
        "social_energy": "medium",
        "vibe_tags": ["happy", "upbeat", "joyful"],
    },
    "sad": {
        "energy": "low",
        "valence": "negative",
        "social_energy": "low",
        "vibe_tags": ["sad", "melancholic", "reflective"],
    },
    "calm": {
        "energy": "low",
        "valence": "neutral",
        "social_energy": "low",
        "vibe_tags": ["calm", "peaceful", "soothing"],
    },
    "anxious": {
        "energy": "medium",
        "valence": "negative",
        "social_energy": "low",
        "vibe_tags": ["anxious", "tense", "restless"],
    },
    "angry": {
        "energy": "high",
        "valence": "negative",
        "social_energy": "low",
        "vibe_tags": ["angry", "intense", "frustrated"],
    },
    "excited": {
        "energy": "very_high",
        "valence": "positive",
        "social_energy": "high",
        "vibe_tags": ["excited", "energetic", "hyped"],
    },
    "romantic": {
        "energy": "medium",
        "valence": "positive",
        "social_energy": "medium",
        "vibe_tags": ["romantic", "tender", "warm"],
    },
    "nostalgic": {
        "energy": "low",
        "valence": "neutral",
        "social_energy": "low",
        "vibe_tags": ["nostalgic", "wistful", "reflective"],
    },
    "neutral": {
        "energy": "medium",
        "valence": "neutral",
        "social_energy": "medium",
        "vibe_tags": ["neutral", "easygoing"],
    },
}
