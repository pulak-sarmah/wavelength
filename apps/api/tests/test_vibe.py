from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_vibe_returns_well_formed_recommendation():
    response = client.post("/vibe", json={"text": "I can't stop smiling, this is the best day ever!"})

    assert response.status_code == 200
    body = response.json()

    vibe = body["vibe"]
    assert vibe["mood"]
    assert vibe["context"] in {"morning", "afternoon", "evening", "night"}
    assert 0.0 <= vibe["confidence"] <= 1.0

    assert isinstance(body["tracks"], list)
    assert len(body["tracks"]) > 0
    assert all({"title", "artist", "provider"} <= track.keys() for track in body["tracks"])

    assert vibe["mood"] in body["explanation"]


def test_vibe_preferences_override_track_limit():
    response = client.post(
        "/vibe",
        json={"text": "I feel great today", "preferences": {"limit": 1}},
    )

    assert response.status_code == 200
    assert len(response.json()["tracks"]) == 1
