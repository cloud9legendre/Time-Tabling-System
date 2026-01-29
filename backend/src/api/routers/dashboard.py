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

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

@router.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request, user: Instructor = Depends(get_current_active_admin), db: Session = Depends(get_db)):
    # 1. Authorization (Role) handled by dependency

    # 3. Fetch Data for Dashboard
    bookings = db.query(Booking).order_by(Booking.booking_date, Booking.start_time).all()
    
    # Fetch ALL resources for the Management Tabs
    all_labs = db.query(Lab).order_by(Lab.id).all()
    # Exclude SUPER_ADMIN from management list to prevent accidental editing/deletion
    all_instructors = db.query(Instructor).filter(Instructor.role != "SUPER_ADMIN").order_by(Instructor.name).all()
    all_modules = db.query(Module).order_by(Module.code).all()
    departments = db.query(Department).order_by(Department.code).all()

    # Filter ACTIVE resources for the Booking Dropdowns
    active_labs = [l for l in all_labs if l.is_active]
    # Allow Instructors AND Admins to be booked
    active_instructors = [i for i in all_instructors if i.is_active and i.role in ["INSTRUCTOR", "ADMIN"]]
    active_modules = [m for m in all_modules if m.is_active]
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request, 
        "user": user,
        "bookings": bookings,
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
