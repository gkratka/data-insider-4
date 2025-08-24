import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from models.user import User

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login():
    # First create a user
    client.post(
        "/users/",
        json={
            "email": "login@example.com",
            "password": "testpassword",
            "full_name": "Login User"
        }
    )
    
    # Then try to login
    response = client.post(
        "/auth/token",
        data={"username": "login@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"