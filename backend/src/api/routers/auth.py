from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from src.database import get_db
from src.models import Instructor
from src.auth.security import create_access_token, verify_password, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.csrf import validate_csrf
from src.auth.dependencies import get_current_user
from src.core.limiter import limiter

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")
logger = logging.getLogger(__name__)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "csrf_token": request.state.csrf_token})

@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db), csrf_protect: None = Depends(validate_csrf)):
    try:
        user = db.query(Instructor).filter(Instructor.email == email).first()
        
        if not user:
            return RedirectResponse(url="/login?error=Invalid Credentials", status_code=303)

        if verify_password(password, user.password):
            # JWT IMPLEMENTATION
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id), "role": user.role},
                expires_delta=access_token_expires
            )
            
            target = "/" if user.role in ["ADMIN", "SUPER_ADMIN"] else "/instructor"
            resp = RedirectResponse(url=target, status_code=303)
            
            resp.set_cookie(
                key="access_token", 
                value=access_token, 
                httponly=True, 
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )
            # Remove legacy insecure cookie if it exists
            resp.delete_cookie("user_id")
            
            return resp
            
        return RedirectResponse(url="/login?error=Invalid Credentials", status_code=303)

    except Exception as e:
        logger.error(f"Login Error: {e}")
        return RedirectResponse(url=f"/login?error=System Error: {str(e)}", status_code=303)

@router.post("/auth/change-password")
def change_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    user: Instructor = Depends(get_current_user),
    csrf_protect: None = Depends(validate_csrf)
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    if new_password != confirm_password:
        referer = request.headers.get("referer", "/instructor")
        return RedirectResponse(url=f"{referer}?error=Passwords do not match", status_code=303)

    if not verify_password(old_password, user.password):
        referer = request.headers.get("referer", "/instructor")
        return RedirectResponse(url=f"{referer}?error=Incorrect current password", status_code=303)

    user.password = get_password_hash(new_password)
    db.commit()
    
    referer = request.headers.get("referer", "/instructor")
    return RedirectResponse(url=f"{referer}?success=Password changed successfully", status_code=303)


@router.post("/auth/reset-password/{user_id}")
def reset_password(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Instructor = Depends(get_current_user),
    csrf_protect: None = Depends(validate_csrf)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    target_user = db.query(Instructor).get(user_id)
    if not target_user:
        return RedirectResponse(url="/?error=User not found", status_code=303)

    # Authorization Logic
    is_authorized = False
    
    # SuperAdmin can reset everyone
    if current_user.role == "SUPER_ADMIN":
        is_authorized = True
    # Admin can reset Instructors only
    elif current_user.role == "ADMIN":
        if target_user.role == "INSTRUCTOR":
            is_authorized = True
            
    if not is_authorized:
        return RedirectResponse(url="/?error=Unauthorized action", status_code=303)

    target_user.password = get_password_hash("password123")
    db.commit()

    return RedirectResponse(url="/?success=Password reset to 'password123'", status_code=303)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
