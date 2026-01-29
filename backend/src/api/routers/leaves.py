from fastapi import APIRouter, Depends, HTTPException, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from src.database import get_db
from src.models import Leave, Instructor
from src.auth.dependencies import get_current_user, get_current_active_admin
from src.auth.csrf import validate_csrf
from starlette.responses import RedirectResponse

router = APIRouter(
    prefix="/leaves",
    tags=["leaves"],
    responses={404: {"description": "Not found"}},
)

@router.post("/request")
def request_leave(
    request: Request,
    start_date: str = Form(...),
    end_date: str = Form(...),
    reason: str = Form(None),
    user: Instructor = Depends(get_current_user),
    db: Session = Depends(get_db),
    csrf: None = Depends(validate_csrf)
):
    # Parse dates
    s_date = date.fromisoformat(start_date)
    e_date = date.fromisoformat(end_date)
    
    if s_date > e_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
        
    # Auto-approve for Admins
    status = "APPROVED" if user.role in ["ADMIN", "SUPER_ADMIN"] else "PENDING"
    
    new_leave = Leave(
        instructor_id=user.id,
        start_date=s_date,
        end_date=e_date,
        reason=reason,
        status=status
    )
    db.add(new_leave)
    db.commit()
    
    # Redirect back to where the request came from (instructor or admin dashboard)
    # Ideally passing a success message param
    referer = request.headers.get("referer")
    if referer:
        if "?" in referer:
            referer = referer.split("?")[0]
        return RedirectResponse(url=f"{referer}?success=Leave+Requested", status_code=303)
    return RedirectResponse(url="/dashboard/instructor?success=Leave+Requested", status_code=303)

@router.post("/{leave_id}/approve")
def approve_leave(
    request: Request,
    leave_id: int,
    user: Instructor = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
    csrf: None = Depends(validate_csrf)
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
        
    leave.status = "APPROVED"
    db.commit()
    
    return RedirectResponse(
        url="/?success=Leave+Approved#leaves", 
        status_code=303
    )

@router.post("/{leave_id}/reject")
def reject_leave(
    request: Request,
    leave_id: int,
    user: Instructor = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
    csrf: None = Depends(validate_csrf)
):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
        
    leave.status = "REJECTED"
    db.commit()
    
    return RedirectResponse(
        url="/?success=Leave+Rejected#leaves", 
        status_code=303
    )
