from vibe_ml import VibePrediction, predict_vibe
from vibe_ml.labels import ENERGY_LABELS, SOCIAL_ENERGY_LABELS, VALENCE_LABELS


def test_predict_vibe_returns_well_formed_prediction():
    prediction = predict_vibe("I can't stop smiling, this is the best day ever!")

    assert isinstance(prediction, VibePrediction)
    assert prediction.energy in ENERGY_LABELS
    assert prediction.valence in VALENCE_LABELS
    assert prediction.social_energy in SOCIAL_ENERGY_LABELS
    assert 0.0 <= prediction.confidence <= 1.0
    assert prediction.vibe_tags


def test_predict_vibe_derived_fields_match_mood_lookup():
    """energy/valence/social_energy/vibe_tags must come from MOOD_TO_DERIVED
    for whatever mood was predicted — this is a rule lookup, not a second
    model, so it should never disagree with the table."""
    from vibe_ml.labels import MOOD_TO_DERIVED

    prediction = predict_vibe("I'm so nervous about tomorrow's exam I can barely breathe.")
    expected = MOOD_TO_DERIVED[prediction.mood]

    assert prediction.energy == expected["energy"]
    assert prediction.valence == expected["valence"]
    assert prediction.social_energy == expected["social_energy"]
    assert prediction.vibe_tags == expected["vibe_tags"]
