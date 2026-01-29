from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.responses import RedirectResponse

from ..database import get_db
from ..models import Instructor
from .security import verify_token

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[Instructor]:
    """
    Extracts the JWT from the 'access_token' cookie, verifies it,
    and returns the corresponding Instructor (User).
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None
        
    user = db.query(Instructor).get(int(user_id))
    return user

def get_current_active_admin(user: Optional[Instructor] = Depends(get_current_user)) -> Instructor:
    """
    Enforces that the user is logged in AND is an ADMIN or SUPER_ADMIN.
    If not, raises HTTPException(403) or redirects depending on API type.
    For this application, we want to enforce redirect to login or show error.
    However, Depends usually raises generic HTTPExceptions for API flows.
    """
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    if user.role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
        
    return user
