from copy import deepcopy

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_data():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_student_to_activity():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "student@example.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_is_rejected():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_student_from_activity():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "student@example.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert delete_response.status_code == 200

    response = client.get("/activities")
    assert response.status_code == 200
    assert email not in response.json()[activity_name]["participants"]
