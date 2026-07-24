import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

initial_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all(client):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.json() == initial_activities


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = initial_activities[activity_name]["participants"][0]
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_returns_success(client):
    # Arrange
    activity_name = "Programming Class"
    email = initial_activities[activity_name]["participants"][0]
    url = f"/activities/{quote(activity_name)}/signup"

    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Programming Class"
    email = "not_signed_up@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
