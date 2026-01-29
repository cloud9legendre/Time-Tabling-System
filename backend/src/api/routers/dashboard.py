from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response as FileResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from src.database import get_db
from src.models import Booking, Lab, Instructor, Module, Department
from src.auth.dependencies import get_current_user, get_current_active_admin
from src.export import generate_ics
import calendar
from sqlalchemy import extract

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request, 
    year: Optional[int] = None,
    month: Optional[int] = None,
    user: Instructor = Depends(get_current_active_admin), 
    db: Session = Depends(get_db)
):
    # 1. Date Navigation Logic
    today = date.today()
    if not year: year = today.year
    if not month: month = today.month

    # Normalize month
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    # Calculate Prev/Next for UI
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    # 2. Calendar Matrix
    # monthcalendar returns list of weeks, each week is list of days (0 for padding)
    calendar_weeks = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # 3. Fetch Data for Dashboard (Calendar Scoped)
    # Filter bookings for the selected month/year only
    calendar_bookings = db.query(Booking).filter(
        extract('month', Booking.booking_date) == month,
        extract('year', Booking.booking_date) == year
    ).order_by(Booking.booking_date, Booking.start_time).all()
    
    bookings_by_date = {}
    for b in calendar_bookings:
        d_str = b.booking_date.isoformat()
        if d_str not in bookings_by_date:
            bookings_by_date[d_str] = []
        bookings_by_date[d_str].append(b)

    # 4. Fetch Management Data (ALL) for other tabs
    bookings_list = db.query(Booking).order_by(Booking.booking_date, Booking.start_time).all()
    
    all_labs = db.query(Lab).order_by(Lab.id).all()
    all_instructors = db.query(Instructor).filter(Instructor.role != "SUPER_ADMIN").order_by(Instructor.name).all()
    all_modules = db.query(Module).order_by(Module.code).all()
    departments = db.query(Department).order_by(Department.code).all()

    # Filter ACTIVE resources
    active_labs = [l for l in all_labs if l.is_active]
    # Allow Instructors AND Admins to be booked
    active_instructors = [i for i in all_instructors if i.is_active and i.role in ["INSTRUCTOR", "ADMIN"]]
    active_modules = [m for m in all_modules if m.is_active]
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request, 
        "user": user,
        
        # Calendar Data
        "year": year,
        "month": month,
        "month_name": month_name,
        "calendar_weeks": calendar_weeks,
        "bookings_by_date": bookings_by_date,
        "prev_year": prev_year, "prev_month": prev_month,
        "next_year": next_year, "next_month": next_month,
        "today_str": today.isoformat(),
        
        # Management Data
        "bookings": bookings_list,
        "all_labs": all_labs, 
        "all_instructors": all_instructors, 
        "all_modules": all_modules,
        "departments": departments,
        "active_labs": active_labs, 
        "active_instructors": active_instructors, 
        "active_modules": active_modules,
        "csrf_token": request.state.csrf_token
    })

@router.get("/instructor", response_class=HTMLResponse)
def instructor_dash(request: Request, user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    
    schedule = db.query(Booking).filter(
        Booking.booked_by_id == user.id
    ).order_by(
        Booking.booking_date.asc(), 
        Booking.start_time.asc()
    ).all()
    
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request, "user": user, "schedule": schedule, "today": date.today(),
        "csrf_token": request.state.csrf_token
    })

@router.get("/export/ics")
def export_ics_route(user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    bookings = db.query(Booking).filter(Booking.booked_by_id == user.id).all()
    data = generate_ics(bookings, user.email)
    return FileResponse(content=data, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=cal.ics"})
