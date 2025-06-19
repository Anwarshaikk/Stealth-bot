import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil

# Import the main FastAPI app and dependency
from api.main import app
from api.deps import get_redis

client = TestClient(app)

@pytest.mark.parametrize("parser_preference, expected_parser_path", [
    ("pyresparser", "api.routers.resume.ResumeParser"),
    ("docai", "api.services.docai_parser.parse_with_docai"),
    ("gpt-4", "api.services.gpt4_parser.parse_with_gpt4"),
])
def test_upload_resume_dynamic_parser(
    parser_preference,
    expected_parser_path,
    mocker,
    mock_redis_conn
):
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    mock_redis_conn.get.return_value = parser_preference.encode('utf-8')
    mock_parser = mocker.patch(expected_parser_path)
    mock_parser.return_value = {"name": "Test User", "email": "test@example.com", "skills": ["pytest"]}
    dummy_file_content = b"dummy resume content"
    files = {"file": ("test_resume.pdf", dummy_file_content, "application/pdf")}
    response = client.post("/resume/upload", files=files)
    assert response.status_code == 201
    mock_parser.assert_called_once()
    mock_redis_conn.set.assert_called_once()
    call_args = mock_redis_conn.set.call_args[0]
    assert call_args[0].startswith("candidate:")
    assert '"name": "Test User"' in call_args[1]
    app.dependency_overrides = {}

def test_upload_resume_default_parser(mocker, mock_redis_conn):
    """Test that pyresparser is used as default when no preference is set."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    
    # Mock Redis to return None (no preference set)
    mock_redis_conn.get.return_value = None
    
    # Mock pyresparser
    mock_parser = mocker.patch("api.routers.resume.ResumeParser")
    mock_parser_instance = MagicMock()
    mock_parser_instance.get_extracted_data.return_value = {
        "name": "Default User",
        "email": "default@example.com",
        "skills": ["default"],
        "mobile_number": "123-456-7890",
        "experience": [],
        "education": []
    }
    mock_parser.return_value = mock_parser_instance

    # Mock file operations
    with patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.read.return_value = b"dummy resume content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch('os.makedirs'):
            with patch('os.rename'):
                files = {"file": ("test_resume.pdf", b"dummy content", "application/pdf")}
                
                # --- Act ---
                response = client.post("/resume/upload", files=files)

    # --- Assert ---
    assert response.status_code == 201
    mock_parser.assert_called_once()
    
    response_data = response.json()
    assert response_data["name"] == "Default User"
    
    app.dependency_overrides = {}

def test_upload_resume_parser_error(mocker, mock_redis_conn):
    """Test error handling when parser fails."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    mock_redis_conn.get.return_value = "pyresparser".encode('utf-8')
    
    # Mock parser to raise an exception
    mock_parser = mocker.patch("api.routers.resume.ResumeParser")
    mock_parser_instance = MagicMock()
    mock_parser_instance.get_extracted_data.side_effect = Exception("Parser failed")
    mock_parser.return_value = mock_parser_instance

    # Mock file operations
    with patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.read.return_value = b"dummy resume content"
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch('os.makedirs'):
            with patch('os.rename'):
                files = {"file": ("test_resume.pdf", b"dummy content", "application/pdf")}
                
                # --- Act ---
                response = client.post("/resume/upload", files=files)

    # --- Assert ---
    assert response.status_code == 500
    assert "Error parsing resume" in response.json()["detail"]
    
    app.dependency_overrides = {}

def test_upload_resume_file_error(mocker, mock_redis_conn):
    """Test error handling when file operations fail."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    
    # Mock file operations to raise an exception
    with patch('builtins.open', create=True, side_effect=Exception("File error")):
        files = {"file": ("test_resume.pdf", b"dummy content", "application/pdf")}
        
        # --- Act ---
        response = client.post("/resume/upload", files=files)

    # --- Assert ---
    assert response.status_code == 500
    assert "Error processing resume upload" in response.json()["detail"]
    
    app.dependency_overrides = {}

def test_list_candidates(mock_redis_conn):
    """Test the list candidates endpoint."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    
    # Mock Redis to return candidate data
    mock_redis_conn.keys.return_value = [b"candidate:123", b"candidate:456"]
    mock_redis_conn.get.side_effect = [
        b'{"candidate_id": "123", "name": "User 1", "email": "user1@test.com", "skills": ["python"]}',
        b'{"candidate_id": "456", "name": "User 2", "email": "user2@test.com", "skills": ["java"]}'
    ]
    
    # --- Act ---
    response = client.get("/resume/")
    
    # --- Assert ---
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) == 2
    assert candidates[0]["name"] == "User 1"
    assert candidates[1]["name"] == "User 2"
    
    app.dependency_overrides = {}

def test_get_candidate(mock_redis_conn):
    """Test the get specific candidate endpoint."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    
    candidate_data = {
        "candidate_id": "123",
        "name": "Test User",
        "email": "test@example.com",
        "skills": ["python", "fastapi"],
        "mobile_number": "123-456-7890",
        "experience": [],
        "education": [],
        "status": "Pending"
    }
    
    mock_redis_conn.get.return_value = str(candidate_data).replace("'", '"').encode('utf-8')
    
    # --- Act ---
    response = client.get("/resume/123")
    
    # --- Assert ---
    assert response.status_code == 200
    candidate = response.json()
    assert candidate["candidate_id"] == "123"
    assert candidate["name"] == "Test User"
    assert candidate["email"] == "test@example.com"
    
    app.dependency_overrides = {}

def test_get_candidate_not_found(mock_redis_conn):
    """Test the get candidate endpoint when candidate doesn't exist."""
    # --- Arrange ---
    app.dependency_overrides[get_redis] = lambda: mock_redis_conn
    mock_redis_conn.get.return_value = None
    
    # --- Act ---
    response = client.get("/resume/nonexistent")
    
    # --- Assert ---
    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"
    
    app.dependency_overrides = {}
