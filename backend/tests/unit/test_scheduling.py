import pytest
from unittest.mock import MagicMock
from datetime import date, time
from src.scheduling import SchedulingService
from src.models import Booking

def test_hard_conflict_outside_hours():
    mock_db = MagicMock()
    scheduler = SchedulingService(mock_db)
    
    # 07:00 is too early (Start is 08:00)
    errors = scheduler.check_hard_conflicts(1, 1, date.today(), time(7, 0), time(9, 0))
    assert "Outside operating hours" in errors[0]

def test_hard_conflict_overlap():
    mock_db = MagicMock()
    scheduler = SchedulingService(mock_db)
    
    # Mocking the query chain: db.query().filter().first() returns a Booking
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    
    # Simulate existing booking
    existing_booking = Booking(start_time=time(9,0), end_time=time(10,0))
    mock_filter.first.return_value = existing_booking
    
    errors = scheduler.check_hard_conflicts(1, 1, date.today(), time(9, 30), time(10, 30))
    assert "Lab collision" in errors[0]

def test_no_conflict():
    mock_db = MagicMock()
    scheduler = SchedulingService(mock_db)
    
    mock_query = mock_db.query.return_value
    mock_filter = mock_query.filter.return_value
    
    # Simulate NO existing booking
    mock_filter.first.return_value = None
    
    errors = scheduler.check_hard_conflicts(1, 1, date.today(), time(10, 0), time(11, 0))
    assert len(errors) == 0
