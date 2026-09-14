from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import RecommendationResponse
from app.schemas.vibe import VibeRequest
from app.services.vibe_service import get_vibe_recommendation

router = APIRouter()


@router.post("/vibe", response_model=RecommendationResponse)
def create_vibe_recommendation(request: VibeRequest, db: Session = Depends(get_db)) -> RecommendationResponse:
    """Understand the user's vibe from text and return song recommendations.

    Optional photo upload will be added as a separate multipart endpoint
    once the text-only pipeline is settled.
    """
    return get_vibe_recommendation(request.text, request.preferences, db)
