from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uuid
import logging

from src.database import get_db
from src.models import Booking, Lab, Instructor, Module
from src.auth.dependencies import get_current_user, get_current_active_admin
from src.auth.csrf import validate_csrf
from src.scheduling import SchedulingService

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")
logger = logging.getLogger(__name__)

@router.post("/bookings/create")
def create_booking(
    lab_id: int = Form(...), 
    instructor_id: int = Form(...), 
    module_code: str = Form(...),
    practical_name: str = Form(""),
    booking_date: str = Form(...), 
    start_time: str = Form(...), 
    end_time: str = Form(...),
    is_recurring: Optional[bool] = Form(False),
    repeat_until: Optional[str] = Form(None),
    user: Optional[Instructor] = Depends(get_current_user),
    db: Session = Depends(get_db),
    csrf_protect: None = Depends(validate_csrf)
):
    # Auth Check
    if not user: return RedirectResponse("/login", status_code=303)
    if user.role not in ["ADMIN", "SUPER_ADMIN"]:
        return RedirectResponse("/instructor", status_code=303)

    try:
        # Parse Base Inputs
        first_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        s_time = datetime.strptime(start_time, "%H:%M").time()
        e_time = datetime.strptime(end_time, "%H:%M").time()
        
        # 1. Generate List of Dates
        target_dates = [first_date]
        
        if is_recurring and repeat_until:
            end_date = datetime.strptime(repeat_until, "%Y-%m-%d").date()
            if end_date <= first_date:
                 return RedirectResponse(url="/?error=Repeat date must be after start date", status_code=303)
            
            current_date = first_date + timedelta(days=7)
            while current_date <= end_date:
                target_dates.append(current_date)
                current_date += timedelta(days=7)
        
        # 2. Validation Loop (Atomic Check)
        scheduler = SchedulingService(db)
        
        for check_date in target_dates:
            errors = scheduler.check_hard_conflicts(lab_id, instructor_id, check_date, s_time, e_time)
            if errors:
                return RedirectResponse(
                    url=f"/?error=Conflict on {check_date}: {errors[0]} (Series Cancelled)", 
                    status_code=303
                )
        
        # 3. Creation Loop
        series_uuid = uuid.uuid4() if len(target_dates) > 1 else None
        
        for book_date in target_dates:
            new_booking = Booking(
                lab_id=lab_id, 
                booked_by_id=instructor_id, 
                module_code=module_code,
                practical_name=practical_name,
                booking_date=book_date,
                start_time=s_time, 
                end_time=e_time, 
                status="APPROVED",
                series_id=series_uuid
            )
            db.add(new_booking)
            
        db.commit()
        return RedirectResponse(url=f"/?success=Created {len(target_dates)} sessions successfully", status_code=303)

    except ValueError:
        return RedirectResponse(url="/?error=Invalid Date/Time Format", status_code=303)
    except Exception as e:
        logger.error(f"Booking Error: {e}")
        return RedirectResponse(url=f"/?error=System Error: {str(e)}", status_code=303)

@router.post("/bookings/delete/{booking_id}")
def delete_booking(booking_id: str, user: Instructor = Depends(get_current_active_admin), db: Session = Depends(get_db), csrf_protect: None = Depends(validate_csrf)):
    # Auth Check handled by dependency

    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            db.delete(booking)
            db.commit()
            return RedirectResponse(url="/?success=Booking Deleted", status_code=303)
        return RedirectResponse(url="/?error=Booking Not Found", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/?error=Delete Failed: {str(e)}", status_code=303)

@router.get("/bookings/edit/{booking_id}", response_class=HTMLResponse)
def edit_booking_page(request: Request, booking_id: str, user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login", status_code=303)
    
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b: return RedirectResponse(url="/?error=Not found", status_code=303)
    
    return templates.TemplateResponse("edit_booking.html", {
        "request": request, "booking": b,
        "labs": db.query(Lab).filter(Lab.is_active==True).all(),
        # Allow INSTRUCTOR and ADMIN in edit dropdown
        "instructors": db.query(Instructor).filter(Instructor.role.in_(["INSTRUCTOR", "ADMIN"]), Instructor.is_active==True).all(),
        "modules": db.query(Module).filter(Module.is_active==True).all(),
        "csrf_token": request.state.csrf_token
    })

@router.post("/bookings/update/{booking_id}")
def update_booking(
    booking_id: str,
    lab_id: int = Form(...), 
    instructor_id: int = Form(...), 
    module_code: str = Form(...),
    practical_name: str = Form(""),
    booking_date: str = Form(...), 
    start_time: str = Form(...), 
    end_time: str = Form(...),
    user: Optional[Instructor] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user: return RedirectResponse("/login", status_code=303)
    
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return RedirectResponse(url="/?error=Booking not found", status_code=303)
        
        booking.lab_id = lab_id
        booking.booked_by_id = instructor_id
        booking.module_code = module_code
        booking.practical_name = practical_name
        
        booking.booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        booking.start_time = datetime.strptime(start_time[:5], "%H:%M").time()
        booking.end_time = datetime.strptime(end_time[:5], "%H:%M").time()
        
        db.commit()
        return RedirectResponse(url="/?success=Booking Updated", status_code=303)

    except ValueError as ve:
        return RedirectResponse(url=f"/?error=Invalid Date/Time Format: {str(ve)}", status_code=303)
    except Exception as e:
        logger.error(f"Update Error: {e}")
        return RedirectResponse(url=f"/?error=Update Failed: {str(e)}", status_code=303)
