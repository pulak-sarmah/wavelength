"""SQLAlchemy models.

Placeholder — will store past vibe queries and their recommendations so
we can look at real usage during error analysis and, later, build a
personalization/history feature in the UI.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VibeQuery(Base):
    __tablename__ = "vibe_queries"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String)
    mood: Mapped[str] = mapped_column(String)
    energy: Mapped[str] = mapped_column(String)
    valence: Mapped[str] = mapped_column(String)
    context: Mapped[str] = mapped_column(String)
    social_energy: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
