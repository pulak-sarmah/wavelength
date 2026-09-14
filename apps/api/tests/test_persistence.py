import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, VibeQuery
from app.db.session import get_db
from app.main import app

# An isolated in-memory DB (shared across connections via StaticPool) so
# this test never touches the real vibe.db.
_engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Base.metadata.create_all(bind=_engine)

_SAMPLE_TEXT = "test_persistence: a uniquely identifiable sample string"


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        del app.dependency_overrides[get_db]


def test_vibe_request_is_persisted(client):
    response = client.post("/vibe", json={"text": _SAMPLE_TEXT})
    assert response.status_code == 200
    mood = response.json()["vibe"]["mood"]

    db = _TestSession()
    try:
        rows = db.query(VibeQuery).filter(VibeQuery.text == _SAMPLE_TEXT).all()
        assert len(rows) == 1
        assert rows[0].mood == mood
        assert rows[0].created_at is not None
    finally:
        db.close()
