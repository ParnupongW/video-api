from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_list_videos():
    response = client.get("/videos")
    assert response.status_code == 200
    assert "count" in response.json()

def test_get_video_not_found():
    response = client.get("/videos/99999")
    assert response.status_code == 404

def test_get_video_str():
    response = client.get("/videos/abc")
    assert response.status_code == 422

def test_post_video_not_token():
    response = client.post("/videos", json={"title": "TestPost", "views": 500, "likes": 50})
    assert response.status_code == 401

def test_post_video_with_token():
    login = client.post("/login", data={"username": "gundam", "password": "test1234"})
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/videos", json={"title": "TestPost", "views": 500, "likes": 50}, headers=headers)
    assert response.status_code == 201

    new_id = response.json()["id"]
    client.delete(f"/videos/{new_id}", headers=headers)