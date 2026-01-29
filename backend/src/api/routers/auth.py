from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from src.database import get_db
from src.models import Instructor
from src.auth.security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.csrf import validate_csrf
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

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
