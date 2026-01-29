from datetime import date, time, datetime, timedelta
from typing import List, Dict
from ..models import Booking, Lab, Module

class SchedulingService:
    def __init__(self, db):
        self.db = db

    def check_hard_conflicts(self, lab_id, instructor_id, booking_date, start, end):
        errors = []
        if start < time(8, 0) or end > time(17, 0):
            errors.append("Outside operating hours (08:00-17:00)")
        
        # Check Lab Overlap
        overlap = self.db.query(Booking).filter(
            Booking.lab_id == lab_id,
            Booking.booking_date == booking_date,
            Booking.status != "CANCELLED",
            Booking.start_time < end,
            Booking.end_time > start
        ).first()
        if overlap: errors.append(f"Lab collision: {overlap.start_time}-{overlap.end_time}")
        
        return errors

    def find_alternatives(self, lab_id, booking_date, duration_mins):
        # Simplified suggestion logic
        suggestions = []
        lab = self.db.query(Lab).get(lab_id)
        for i in range(1, 4): # Check next 3 days
            next_day = booking_date + timedelta(days=i)
            suggestions.append({
                "date": next_day.isoformat(),
                "start": "08:00",
                "end": "10:00",
                "lab_name": lab.name
            })
        return suggestions
