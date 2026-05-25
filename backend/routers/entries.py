from datetime import datetime, timedelta

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import MoodEntry
from schemas import EntryCreate, EntryResponse, StatsResponse
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.post("/", response_model=EntryResponse, status_code=201)
def create_entry(data: EntryCreate, db: Session = Depends(get_db)):
    entry = MoodEntry(mood=data.mood, note=data.note)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/", response_model=list[EntryResponse])
def list_entries(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    entries = (
        db.query(MoodEntry)
        .filter(MoodEntry.created_at >= since)
        .order_by(MoodEntry.created_at.desc())
        .all()
    )
    return entries


@router.get("/stats", response_model=StatsResponse)
def get_stats(days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    entries = db.query(MoodEntry).filter(MoodEntry.created_at >= since).all()

    if not entries:
        return StatsResponse(total_entries=0, average_mood=None, mood_counts={})

    mood_counts = {}
    total = 0
    for entry in entries:
        mood_counts[entry.mood] = mood_counts.get(entry.mood, 0) + 1
        total += entry.mood

    return StatsResponse(
        total_entries=len(entries),
        average_mood=round(total / len(entries), 2),
        mood_counts=mood_counts,
    )


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(MoodEntry).filter(MoodEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    db.delete(entry)
    db.commit()
