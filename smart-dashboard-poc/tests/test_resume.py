import os
import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def fake_resume_path():
    return os.path.join(os.path.dirname(__file__), "fixtures", "fake_resume.pdf")

@patch("api.routers.resume.affinda_client.create_resume")
def test_post_resume(mock_create_resume, client, fake_resume_path):
    # Mock Affinda response
    mock_create_resume.return_value.as_dict.return_value = {
        "data": {
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
            "profession": {"value": "Software Engineer"},
            "location": {"text": "Remote"},
            "work_experience": ["Company A", "Company B"]
        }
    }
    with open(fake_resume_path, "rb") as f:
        response = client.post("/resume", files={"file": ("fake_resume.pdf", f, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    assert "candidate_id" in data 