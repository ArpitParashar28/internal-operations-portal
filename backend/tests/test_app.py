import os
os.environ["DATABASE_URL"] = "sqlite:///./test_operations.db"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_register_and_login():
    client.post("/auth/register", json={"name":"Test User","email":"test@example.com","password":"secret123","role":"employee"})
    r = client.post("/auth/login", json={"email":"test@example.com","password":"secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
