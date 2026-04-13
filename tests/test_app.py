from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    backup = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(backup))


def test_get_activities_returns_activity_list():
    client = TestClient(app)
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_success():
    client = TestClient(app)
    response = client.post("/activities/Chess%20Club/signup", params={"email": "new@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@mergington.edu for Chess Club"}
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_email_returns_error():
    client = TestClient(app)
    response = client.post("/activities/Chess%20Club/signup", params={"email": "michael@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success():
    client = TestClient(app)
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json() == {"message": "Unregistered michael@mergington.edu from Chess Club"}
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_from_activity_not_signed_up_returns_error():
    client = TestClient(app)
    response = client.delete("/activities/Chess%20Club/unregister", params={"email": "unknown@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_activity_not_found_returns_404_for_signup():
    client = TestClient(app)
    response = client.post("/activities/Nonexistent%20Club/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
