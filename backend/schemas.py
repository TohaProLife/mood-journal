from datetime import datetime

from pydantic import BaseModel, Field


class EntryCreate(BaseModel):
    mood: int = Field(ge=1, le=5)
    note: str = Field(default="", max_length=1000)


class EntryResponse(BaseModel):
    id: int
    mood: int
    note: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total_entries: int
    average_mood: float | None
    mood_counts: dict[int, int]
