from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def get_token():
    email = f"{uuid.uuid4()}@example.com"
    password = "password123"

    # Register
    client.post(
        "/register",
        json={
            "email": email,
            "password": password
        }
    )

    # Login
    response = client.post(
        "/login",
        data={
            "username": email,
            "password": password
        }
    )

    return response.json()["access_token"]


def test_create_note():
    token = get_token()

    response = client.post(
        "/notes",
        json={
            "title": "My Note",
            "content": "Learning FastAPI"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Note created successfully"


def test_get_notes():
    token = get_token()

    response = client.get(
        "/notes",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())

    assert response.status_code == 200


def test_get_note_by_id():
    token = get_token()

    create = client.post(
        "/notes",
        json={
            "title": "Test Note",
            "content": "Test Content"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    note_id = create.json()["note"]["id"]

    response = client.get(
        f"/notes/{note_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())

    assert response.status_code == 200


def test_update_note():
    token = get_token()

    create = client.post(
        "/notes",
        json={
            "title": "Old Title",
            "content": "Old Content"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    note_id = create.json()["note"]["id"]

    response = client.put(
        f"/notes/{note_id}",
        json={
            "title": "New Title",
            "content": "New Content"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Note updated successfully"


def test_delete_note():
    token = get_token()

    create = client.post(
        "/notes",
        json={
            "title": "Delete Me",
            "content": "Temporary"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    note_id = create.json()["note"]["id"]

    response = client.delete(
        f"/notes/{note_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted successfully"