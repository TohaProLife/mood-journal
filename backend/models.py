from datetime import datetime

from database import Base
from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column


class MoodEntry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mood: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
