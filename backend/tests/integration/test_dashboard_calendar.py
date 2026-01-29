
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.api.main import app
from src.models import Instructor, Department, Booking, Lab, Module
from src.auth.security import get_password_hash, create_access_token
from src.auth.csrf import validate_csrf
from datetime import date, time
import uuid

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_calendar.db"
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
    lab = Lab(id=1, name="Lab1", department_code="CSE", capacity=20)
    module = Module(code="CS101", title="Intro", offering_dept="CSE", semester=1)
    
    db.add(admin)
    db.add(lab)
    db.add(module)
    db.commit()

    # Create Booking in Next Month
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    
    booking = Booking(
        id=uuid.uuid4(),
        lab_id=1,
        module_code="CS101",
        booked_by_id=1,
        booking_date=date(next_year, next_month, 15),
        start_time=time(10, 0),
        end_time=time(12, 0),
        status="CONFIRMED",
        purpose="CLASS",
        practical_name="Lab 01: Intro"
    )
    db.add(booking)
    db.commit()
    
    yield db
    Base.metadata.drop_all(bind=engine)

def get_token_cookies(user_id, role):
    token = create_access_token(data={"sub": str(user_id), "role": role})
    return {"access_token": token}

def test_admin_dashboard_calendar_default(setup_db):
    cookies = get_token_cookies(1, "ADMIN")
    response = client.get("/", cookies=cookies)
    assert response.status_code == 200
    assert "Master Schedule" in response.text
    # Default view might not show next month booking
    
def test_admin_dashboard_calendar_navigation(setup_db):
    cookies = get_token_cookies(1, "ADMIN")
    
    # Navigate to next month where we created a booking
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    
    response = client.get(f"/?month={next_month}&year={next_year}", cookies=cookies)
    assert response.status_code == 200
    
    # Verify booking info is rendered
    assert "CS101" in response.text
    # Verify tooltip structure exists
    assert "booking-tooltip" in response.text
    # Verify practical name is rendered
    assert "Lab 01: Intro" in response.text

