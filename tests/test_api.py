import pytest
from database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestSession = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_create_entry():
    response = client.post("/api/entries/", json={"mood": 4, "note": "тест"})
    assert response.status_code == 201
    data = response.json()
    assert data["mood"] == 4
    assert data["note"] == "тест"
    assert "id" in data


def test_create_entry_without_note():
    response = client.post("/api/entries/", json={"mood": 3})
    assert response.status_code == 201
    assert response.json()["note"] == ""


def test_create_entry_invalid_mood():
    response = client.post("/api/entries/", json={"mood": 0})
    assert response.status_code == 422

    response = client.post("/api/entries/", json={"mood": 6})
    assert response.status_code == 422


def test_list_entries():
    client.post("/api/entries/", json={"mood": 5, "note": "первая"})
    client.post("/api/entries/", json={"mood": 2, "note": "вторая"})

    response = client.get("/api/entries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_entries_empty():
    response = client.get("/api/entries/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_stats():
    client.post("/api/entries/", json={"mood": 5})
    client.post("/api/entries/", json={"mood": 3})
    client.post("/api/entries/", json={"mood": 5})

    response = client.get("/api/entries/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 3
    assert data["average_mood"] == 4.33
    assert data["mood_counts"]["5"] == 2


def test_get_stats_empty():
    response = client.get("/api/entries/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_entries"] == 0
    assert data["average_mood"] is None


def test_delete_entry():
    response = client.post("/api/entries/", json={"mood": 4})
    entry_id = response.json()["id"]

    response = client.delete(f"/api/entries/{entry_id}")
    assert response.status_code == 204

    entries = client.get("/api/entries/").json()
    assert len(entries) == 0


def test_delete_nonexistent():
    response = client.delete("/api/entries/999")
    assert response.status_code == 404
