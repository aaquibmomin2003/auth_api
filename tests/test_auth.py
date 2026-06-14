from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_register():
    email = f"{uuid.uuid4()}@example.com"

    response = client.post(
        "/register",
        json={
            "email": email,
            "password": "password123"
        }
    )

    print("Status:", response.status_code)
    print("Body:", response.json())

    assert response.status_code in [200, 201]
    
def test_login():
    email = f"{uuid.uuid4()}@example.com"

    # Register user first
    client.post(
        "/register",
        json={
            "email": email,
            "password": "password123"
        }
    )

    # Login
    response = client.post(
        "/login",
        data={
            "username": email,
            "password": "password123"
        }
    )

    print(response.json())
    assert response.status_code == 200

def test_me():
    email = f"{uuid.uuid4()}@example.com"

    # Register
    client.post(
        "/register",
        json={
            "email": email,
            "password": "password123"
        }
    )

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": email,
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    # Access protected route
    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    print(response.json())
    assert response.status_code == 200