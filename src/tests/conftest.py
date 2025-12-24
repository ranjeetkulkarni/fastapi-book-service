from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from main import app
from db.main import get_session
from auth.service import UserService
# 1. UPDATE IMPORT: Get the INSTANCE 'access_token_bearer'
from auth.dependencies import access_token_bearer, get_current_user
import uuid
from datetime import datetime

# --- Mock Data ---
def mock_get_token_payload():
    return {
        "user": {
            "user_uid": "7c9e6679-7425-40de-944b-e07fc1f90ae7", 
            "email": "test@example.com",
        },
        "role": "admin",
        "jti": "sample-jti",
        "refresh": False
    }

def mock_get_user_object():
    user = Mock()
    user.role = "admin"
    user.email = "test@example.com"
    user.user_uid = "7c9e6679-7425-40de-944b-e07fc1f90ae7"
    return user

# --- Fixtures ---
@pytest.fixture
def mock_session():
    session = Mock()
    def side_effect_refresh(instance):
        if not getattr(instance, "uid", None):
            instance.uid = uuid.uuid4()
        if not getattr(instance, "created_at", None):
            instance.created_at = datetime.now()
        if not getattr(instance, "updated_at", None):
            instance.updated_at = datetime.now()
        return None
    session.refresh.side_effect = side_effect_refresh
    return session

@pytest.fixture
def mock_user_service(mock_session):
    return UserService(mock_session)

@pytest.fixture
def client(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    
    # 2. CRITICAL FIX: Override the INSTANCE
    app.dependency_overrides[access_token_bearer] = mock_get_token_payload
    
    app.dependency_overrides[get_current_user] = mock_get_user_object
    
    with TestClient(app, base_url="http://localhost:8000") as c:
        yield c
    
    app.dependency_overrides = {}