from datetime import datetime

import pytest
from models import MoodEntry
from pydantic import ValidationError
from schemas import EntryCreate, EntryResponse, StatsResponse


def test_mood_entry_creation():
    entry = MoodEntry(id=1, mood=3, note="нормально", created_at=datetime.utcnow())
    assert entry.mood == 3
    assert entry.note == "нормально"
    assert entry.id == 1


def test_entry_create_schema_valid():
    data = EntryCreate(mood=4, note="хороший день")
    assert data.mood == 4
    assert data.note == "хороший день"


def test_entry_create_schema_defaults():
    data = EntryCreate(mood=1)
    assert data.note == ""


def test_entry_create_schema_invalid_mood():
    with pytest.raises(ValidationError):
        EntryCreate(mood=0)

    with pytest.raises(ValidationError):
        EntryCreate(mood=6)


def test_entry_create_schema_long_note():
    with pytest.raises(ValidationError):
        EntryCreate(mood=3, note="a" * 1001)


def test_entry_response_schema():
    data = EntryResponse(id=1, mood=5, note="", created_at=datetime.utcnow())
    assert data.id == 1
    assert data.mood == 5


def test_stats_response_empty():
    data = StatsResponse(total_entries=0, average_mood=None, mood_counts={})
    assert data.total_entries == 0
    assert data.average_mood is None


def test_stats_response_with_data():
    data = StatsResponse(total_entries=3, average_mood=3.67, mood_counts={3: 1, 4: 2})
    assert data.total_entries == 3
    assert data.average_mood == 3.67
    assert data.mood_counts[4] == 2
