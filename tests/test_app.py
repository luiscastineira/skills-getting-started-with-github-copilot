import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Fixture to reset activities before each test
@pytest.fixture(autouse=True)
def reset_activities():
    # Reset to initial state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis instruction and practice on the school courts",
            "schedule": "Tuesdays, Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "claire@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Theater Club": {
            "description": "Acting, directing, and performing in school productions",
            "schedule": "Tuesdays, Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Mondays, Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ryan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["jessica@mergington.edu", "thomas@mergington.edu"]
        }
    })

@pytest.fixture
def client():
    return TestClient(app)

def test_root_redirect(client):
    # Arrange: No special setup needed

    # Act: GET request to root with no redirects
    response = client.get("/", follow_redirects=False)

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    # Arrange: Activities are reset by fixture

    # Act: GET request to /activities
    response = client.get("/activities")

    # Assert: Returns 200 and correct data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]

def test_signup_success(client):
    # Arrange: Use existing activity
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: POST signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Success and added to participants
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate(client):
    # Arrange: Sign up first
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: 400 error
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity(client):
    # Arrange: Invalid activity name
    activity_name = "Invalid Activity"
    email = "student@mergington.edu"

    # Act: POST signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success(client):
    # Arrange: Sign up first
    activity_name = "Chess Club"
    email = "temp@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: DELETE unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert: Success and removed from participants
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_signed_up(client):
    # Arrange: Activity exists but email not signed up
    activity_name = "Chess Club"
    email = "notsigned@mergington.edu"

    # Act: DELETE unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert: 400 error
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity(client):
    # Arrange: Invalid activity name
    activity_name = "Invalid Activity"
    email = "student@mergington.edu"

    # Act: DELETE unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert: 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]