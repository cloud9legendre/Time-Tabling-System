
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.api.main import app
from src.models import Instructor, Department, Booking, Lab, Module, Leave
from src.auth.security import get_password_hash, create_access_token
from src.auth.csrf import validate_csrf
from datetime import date, time
import uuid

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leaves.db"
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
    
    # Create Resources
    if not db.query(Department).filter_by(code="CSE").first():
        db.add(Department(code="CSE", name="Computer Science"))
    
    admin = Instructor(id=1, email="admin@test.com", name="Admin", role="ADMIN", password=get_password_hash("pass"), department_code="CSE")
    instructor = Instructor(id=2, email="inst@test.com", name="Inst", role="INSTRUCTOR", password=get_password_hash("pass"), department_code="CSE")
    lab = Lab(id=1, name="Lab1", department_code="CSE", capacity=20)
    module = Module(code="CS101", title="Intro", offering_dept="CSE", semester=1)
    
    db.add(admin)
    db.add(instructor)
    db.add(lab)
    db.add(module)
    db.commit()

    yield db
    Base.metadata.drop_all(bind=engine)

def get_token_cookies(user_id, role):
    token = create_access_token(data={"sub": str(user_id), "role": role})
    return {"access_token": token}

def test_leave_request_flow(setup_db):
    # 1. Instructor Requests Leave
    cookies_inst = get_token_cookies(2, "INSTRUCTOR")
    response = client.post("/leaves/request", data={
        "start_date": date.today().isoformat(),
        "end_date": date.today().isoformat(),
        "reason": "Sick"
    }, cookies=cookies_inst, follow_redirects=False)
    assert response.status_code == 303
    
    # Verify Pending in DB
    db = TestingSessionLocal()
    leave = db.query(Leave).filter_by(instructor_id=2).first()
    assert leave is not None
    assert leave.status == "PENDING"
    db.close()

    # 2. Admin Sees Pending Leave
    cookies_admin = get_token_cookies(1, "ADMIN")
    response = client.get("/", cookies=cookies_admin)
    assert response.status_code == 200
    assert "Sick" in response.text
    assert "Pending Leave Requests" in response.text
    
    # 3. Admin Approves Leave
    response = client.post(f"/leaves/{leave.id}/approve", cookies=cookies_admin, follow_redirects=False)
    assert response.status_code == 303
    
    # Verify Approved
    db = TestingSessionLocal()
    leave = db.query(Leave).filter_by(instructor_id=2).first()
    assert leave.status == "APPROVED"
    db.close()

def test_conflict_visuals(setup_db):
    db = TestingSessionLocal()
    
    # Create Booking today for the Instructor (who has approved leave today from prev test)
    booking = Booking(
        id=uuid.uuid4(),
        lab_id=1, module_code="CS101", booked_by_id=2,
        booking_date=date.today(), start_time=time(10,0), end_time=time(12,0),
        status="CONFIRMED"
    )
    db.add(booking)
    db.commit()
    db.close()
    
    # Check Admin Dashboard
    cookies_admin = get_token_cookies(1, "ADMIN")
    response = client.get("/", cookies=cookies_admin)
    
    # Assert Warning
    assert "⚠️" in response.text
    assert "unavailable (on leave)" in response.text
    
    # Assert Conflict Badge Class
    assert "booking-conflict" in response.text
    assert "INSTRUCTOR ON LEAVE" in response.text
