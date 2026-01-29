
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.api.main import app
from src.models import Instructor, Department
from src.auth.security import get_password_hash, create_access_token, verify_password
from src.auth.csrf import validate_csrf

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_password.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[validate_csrf] = lambda: None
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create Dept
    if not db.query(Department).filter_by(code="CSE").first():
        db.add(Department(code="CSE", name="Computer Science"))
    
    # Create Users
    users = [
        Instructor(id=1, email="instructor@test.com", name="Instructor", role="INSTRUCTOR", password=get_password_hash("oldpass"), department_code="CSE"),
        Instructor(id=2, email="admin@test.com", name="Admin", role="ADMIN", password=get_password_hash("adminpass"), department_code="CSE"),
        Instructor(id=3, email="superadmin@test.com", name="SuperAdmin", role="SUPER_ADMIN", password=get_password_hash("superpass"), department_code="CSE"),
        Instructor(id=4, email="otheradmin@test.com", name="OtherAdmin", role="ADMIN", password=get_password_hash("otherpass"), department_code="CSE")
    ]
    
    for u in users:
        if not db.query(Instructor).get(u.id):
            db.add(u)
    
    db.commit()
    yield db
    Base.metadata.drop_all(bind=engine)

def get_token_cookies(user_id, role):
    token = create_access_token(data={"sub": str(user_id), "role": role})
    return {"access_token": token}

def test_instructor_change_password(setup_db):
    # Login as Instructor
    cookies = get_token_cookies(1, "INSTRUCTOR")
    
    # 1. Change Password Success
    response = client.post(
        "/auth/change-password",
        data={
            "old_password": "oldpass",
            "new_password": "newpass",
            "confirm_password": "newpass"
        },
        cookies=cookies,
        follow_redirects=False # Expect redirect 
    )
    assert response.status_code == 303
    assert "success" in response.headers["location"]
    
    # Verify DB update
    db = TestingSessionLocal()
    user = db.query(Instructor).get(1)
    assert verify_password("newpass", user.password)

    # 2. Change Password Fail (Wrong Old)
    response = client.post(
        "/auth/change-password",
        data={
            "old_password": "wrong",
            "new_password": "pass",
            "confirm_password": "pass"
        },
        cookies=cookies,
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "error" in response.headers["location"]

def test_admin_reset_instructor_password(setup_db):
    # Login as Admin (ID 2)
    cookies = get_token_cookies(2, "ADMIN")
    
    # Reset Instructor (ID 1)
    response = client.post(f"/auth/reset-password/1", cookies=cookies, follow_redirects=False)
    assert response.status_code == 303
    assert "success" in response.headers["location"]
    
    # Verify
    db = TestingSessionLocal()
    user = db.query(Instructor).get(1)
    assert verify_password("password123", user.password)

def test_admin_cannot_reset_admin_password(setup_db):
    # Login as Admin (ID 2)
    cookies = get_token_cookies(2, "ADMIN")
    
    # Try Reset Other Admin (ID 4)
    response = client.post(f"/auth/reset-password/4", cookies=cookies, follow_redirects=False)
    assert response.status_code == 303
    assert "error" in response.headers["location"] # Unauthorized

def test_superadmin_can_reset_all(setup_db):
    # Login as SuperAdmin (ID 3)
    cookies = get_token_cookies(3, "SUPER_ADMIN")
    
    # Reset Admin (ID 4)
    response = client.post(f"/auth/reset-password/4", cookies=cookies, follow_redirects=False)
    assert response.status_code == 303
    assert "success" in response.headers["location"]
    
    db = TestingSessionLocal()
    user = db.query(Instructor).get(4)
    assert verify_password("password123", user.password)

def test_admin_change_password(setup_db):
    # Login as Admin (ID 2)
    cookies = get_token_cookies(2, "ADMIN")
    
    # 1. Change Password Success
    response = client.post(
        "/auth/change-password",
        data={
            "old_password": "adminpass",
            "new_password": "newadminpass",
            "confirm_password": "newadminpass"
        },
        cookies=cookies,
        follow_redirects=False 
    )
    assert response.status_code == 303
    assert "success" in response.headers["location"]
    
    # Verify DB update
    db = TestingSessionLocal()
    user = db.query(Instructor).get(2)
    assert verify_password("newadminpass", user.password)


