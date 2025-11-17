"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the /activities endpoint"""

    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data


class TestSignupEndpoint:
    """Test the signup endpoint"""

    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_duplicate(self):
        """Test signup fails when student is already registered"""
        # First signup
        client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
        
        # Second signup with same email
        response = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/Non Existent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_participant_appears_in_activity(self):
        """Test that a signed-up participant appears in the activity"""
        email = "visible@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration"""
        email = "unregister@mergington.edu"
        # First, sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_not_registered(self):
        """Test unregister fails when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_invalid_activity(self):
        """Test unregister fails for non-existent activity"""
        response = client.delete(
            "/activities/Non Existent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_participant_removed_from_activity(self):
        """Test that an unregistered participant is removed from the activity"""
        email = "remove@mergington.edu"
        # Sign up
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Verify participant is in the list
        response = client.get("/activities")
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Programming Class/unregister?email={email}")
        
        # Verify participant is removed
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
