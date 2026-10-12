import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client_and_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app), activities


def test_get_activities_returns_activities(client_and_activities):
    client, activities = client_and_activities

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client_and_activities):
    client, activities = client_and_activities
    email = "new@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client_and_activities):
    client, activities = client_and_activities
    email = "existing@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client_and_activities):
    client, _ = client_and_activities

    response = client.post("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client_and_activities):
    client, activities = client_and_activities
    email = "existing@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert activities["Chess Club"]["participants"] == []


def test_unregister_rejects_participant_not_signed_up(client_and_activities):
    client, activities = client_and_activities
    email = "unknown@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_unregister_rejects_unknown_activity(client_and_activities):
    client, _ = client_and_activities

    response = client.delete("/activities/Unknown/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"