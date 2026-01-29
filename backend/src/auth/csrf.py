import secrets
from fastapi import Request, HTTPException, status, Form

CSRF_COOKIE_NAME = "csrf_token"
CSRF_FORM_FIELD_NAME = "csrf_token"

def generate_csrf_token() -> str:
    """Generates a secure random 32-byte hex string."""
    return secrets.token_hex(32)

def validate_csrf(request: Request, csrf_token: str = Form(None)):
    """
    Dependency to validate CSRF token on POST requests.
    Checks if the cookie token matches the form token.
    """
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    
    if not cookie_token or not csrf_token or cookie_token != csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF Token Validation Failed. Please refresh the page."
        )
