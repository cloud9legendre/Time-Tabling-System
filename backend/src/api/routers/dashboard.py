from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response as FileResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from src.database import get_db
from src.models import Booking, Lab, Instructor, Module, Department, Leave
from src.auth.dependencies import get_current_user, get_current_active_admin
from src.export import generate_ics
import calendar
from sqlalchemy import extract

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

def get_calendar_context(db: Session, year: Optional[int] = None, month: Optional[int] = None):
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
    calendar_weeks = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # 3. Fetch Data for Dashboard (Calendar Scoped)
    calendar_bookings = db.query(Booking).filter(
        extract('month', Booking.booking_date) == month,
        extract('year', Booking.booking_date) == year
    ).order_by(Booking.booking_date, Booking.start_time).all()
    
    # 2b. Fetch Approved Leaves for Conflict Checking & Calendar Display
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    
    approved_leaves = db.query(Leave).filter(
        Leave.status == "APPROVED",
        Leave.end_date >= month_start,
        Leave.start_date <= month_end
    ).all()
    
    # Map instructor_id -> list of (start, end)
    leave_map = {}
    
    # NEW: Map date -> list of approved leaves (for calendar display)
    leaves_by_date = {}

    for l in approved_leaves:
        if l.instructor_id not in leave_map: leave_map[l.instructor_id] = []
        leave_map[l.instructor_id].append((l.start_date, l.end_date))
        
        # Populate leaves_by_date logic: explode range
        curr = l.start_date
        while curr <= l.end_date:
            # Check if curr is in this month
            if curr.year == year and curr.month == month:
                d_str = curr.isoformat()
                if d_str not in leaves_by_date: leaves_by_date[d_str] = []
                leaves_by_date[d_str].append(l)
            curr = curr.replace(day=curr.day + 1) if curr.day < calendar.monthrange(curr.year, curr.month)[1] else (curr.replace(month=curr.month+1, day=1) if curr.month < 12 else curr.replace(year=curr.year+1, month=1, day=1))
            # Rough increment logic for day loop, simpler: timedelta
            # Actually easier to use python date math but standard lib:
            from datetime import timedelta
            curr += timedelta(days=1)
            # wait, I already did curr += ... using logic above. but the logic above is messy.
            # let's reset and use timedelta, need to import it properly or use existing imports
            # 'from datetime import date' is there. let's add timedelta to line 5. 

    unavailable_instructors = set()

    bookings_by_date = {}
    for b in calendar_bookings:
        # Check conflict
        is_conflict = False
        if b.booked_by_id in leave_map:
            for start, end in leave_map[b.booked_by_id]:
                if start <= b.booking_date <= end:
                    is_conflict = True
                    unavailable_instructors.add(b.booked_by_id)
                    break
        b.is_conflict = is_conflict 

        d_str = b.booking_date.isoformat()
        if d_str not in bookings_by_date:
            bookings_by_date[d_str] = []
        bookings_by_date[d_str].append(b)

    return {
        "year": year,
        "month": month,
        "month_name": month_name,
        "calendar_weeks": calendar_weeks,
        "bookings_by_date": bookings_by_date,
        "leaves_by_date": leaves_by_date, # EXPOSED
        "prev_year": prev_year, "prev_month": prev_month,
        "next_year": next_year, "next_month": next_month,
        "today_str": today.isoformat(),
        "unavailable_instructors_count": len(unavailable_instructors)
    }

@router.get("/health", status_code=200)
def health_check():
    return {"status": "healthy"}

@router.get("/calendar/fragment", response_class=HTMLResponse) # NEW ENDPOINT
def get_calendar_fragment(
    request: Request,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    ctx = get_calendar_context(db, year, month)
    return templates.TemplateResponse("partials/calendar_grid.html", {
        "request": request,
        **ctx
    })

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(
    request: Request, 
    year: Optional[int] = None,
    month: Optional[int] = None,
    user: Instructor = Depends(get_current_active_admin), 
    db: Session = Depends(get_db)
):
    calendar_ctx = get_calendar_context(db, year, month)
    
    pending_leaves = db.query(Leave).filter(Leave.status == "PENDING").all()
    pending_count = len(pending_leaves)

    processed_leaves = db.query(Leave).filter(Leave.status != "PENDING").order_by(Leave.start_date.desc()).all()

    bookings_list = db.query(Booking).order_by(Booking.booking_date, Booking.start_time).all()
    
    all_labs = db.query(Lab).order_by(Lab.id).all()
    all_instructors = db.query(Instructor).filter(Instructor.role != "SUPER_ADMIN").order_by(Instructor.name).all()
    all_modules = db.query(Module).order_by(Module.code).all()
    departments = db.query(Department).order_by(Department.code).all()

    active_labs = [l for l in all_labs if l.is_active]
    active_instructors = [i for i in all_instructors if i.is_active and i.role in ["INSTRUCTOR", "ADMIN"]]
    active_modules = [m for m in all_modules if m.is_active]
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request, 
        "user": user,
        **calendar_ctx,
        "bookings": bookings_list,
        "all_labs": all_labs, 
        "all_instructors": all_instructors, 
        "all_modules": all_modules,
        "departments": departments,
        "active_labs": active_labs, 
        "active_instructors": active_instructors, 
        "active_modules": active_modules,
        "csrf_token": request.state.csrf_token,
        "pending_leaves": pending_leaves,
        "pending_count": pending_count,
        "processed_leaves": processed_leaves
    })

@router.get("/instructor", response_class=HTMLResponse)
def instructor_dash(
    request: Request, 
    year: Optional[int] = None,
    month: Optional[int] = None,
    user: Optional[Instructor] = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not user: return RedirectResponse("/login")
    
    calendar_ctx = get_calendar_context(db, year, month)

    schedule = db.query(Booking).filter(
        Booking.booked_by_id == user.id
    ).order_by(
        Booking.booking_date.asc(), 
        Booking.start_time.asc()
    ).all()

    my_leaves = db.query(Leave).filter(Leave.instructor_id == user.id).order_by(Leave.start_date.desc()).all()
    
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request, 
        "user": user, 
        "schedule": schedule, 
        "my_leaves": my_leaves, 
        "today": date.today(),
        "csrf_token": request.state.csrf_token,
        **calendar_ctx
    })

@router.get("/export/ics")
def export_ics_route(user: Optional[Instructor] = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user: return RedirectResponse("/login")
    bookings = db.query(Booking).filter(Booking.booked_by_id == user.id).all()
    data = generate_ics(bookings, user.email)
    return FileResponse(content=data, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=cal.ics"})
