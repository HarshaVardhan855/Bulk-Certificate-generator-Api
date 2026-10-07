from fastapi.testclient import TestClient


def test_validation_invalid_email(client: TestClient):
    """Test validation fails for invalid email address."""
    payload = {
        "event_name": "Python Conference",
        "certificate_date": "2026-10-07",
        "recipients": [
            {"name": "Valid Name", "email": "invalid-email-address", "course": "Python"}
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_recipient_name(client: TestClient):
    """Test validation fails for empty or whitespace-only recipient name."""
    payload = {
        "event_name": "Python Conference",
        "certificate_date": "2026-10-07",
        "recipients": [
            {"name": "   ", "email": "valid@example.com", "course": "Python"}
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_event_name(client: TestClient):
    """Test validation fails for empty or whitespace-only event name."""
    payload = {
        "event_name": "   ",
        "certificate_date": "2026-10-07",
        "recipients": [
            {"name": "Valid Name", "email": "valid@example.com", "course": "Python"}
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_recipients_list(client: TestClient):
    """Test validation fails for empty recipients list."""
    payload = {
        "event_name": "Python Conference",
        "certificate_date": "2026-10-07",
        "recipients": [],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_validation_invalid_date_format(client: TestClient):
    """Test validation fails for invalid certificate date."""
    payload = {
        "event_name": "Python Conference",
        "certificate_date": "2026/10/07",  # Not ISO YYYY-MM-DD
        "recipients": [
            {"name": "Valid Name", "email": "valid@example.com", "course": "Python"}
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422

    # Malformed string
    payload["certificate_date"] = "invalid-date"
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422


def test_validation_empty_course(client: TestClient):
    """Test validation fails for empty course name."""
    payload = {
        "event_name": "Python Conference",
        "certificate_date": "2026-10-07",
        "recipients": [
            {"name": "Valid Name", "email": "valid@example.com", "course": "   "}
        ],
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422
