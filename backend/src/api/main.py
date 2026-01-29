from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
import logging
import uuid
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from ..database import engine, Base
from ..auth.csrf import generate_csrf_token, CSRF_COOKIE_NAME
from ..core.limiter import limiter
from .routers import auth, dashboard, resources, bookings, leaves

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Tables (will be redundant with Alembic later, but kept for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CLTS")
app.state.limiter = limiter

# Middleware & Exception Handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_csrf_cookie(request: Request, call_next):
    csrf_token = request.cookies.get(CSRF_COOKIE_NAME)
    new_token = False
    if not csrf_token:
        csrf_token = generate_csrf_token()
        new_token = True
    
    request.state.csrf_token = csrf_token
    response = await call_next(request)
    
    if new_token:
        response.set_cookie(key=CSRF_COOKIE_NAME, value=csrf_token, httponly=True, path="/")
    return response

@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login?error=Session Expired or Login Required", status_code=303)
    if exc.status_code == 403:
        return RedirectResponse(url="/instructor?error=Access Denied", status_code=303)
    return HTMLResponse(content=f"<h1>Error {exc.status_code}: {exc.detail}</h1>", status_code=exc.status_code)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Don't catch HTTPExceptions here, let auth_exception_handler handle them
    if isinstance(exc, HTTPException):
        raise exc # Re-raise to let other handlers catch it, but we are inside an exception handler...
        # Actually starlette handles this if we return None? No. 
        # If we registered HTTPException handler, it catches it FIRST if it matches.
        # But this is "Exception", base class.
    
    logger.error(f"Global Error: {exc}", exc_info=True)
    if "admin" in request.url.path or "login" in request.url.path:
         return RedirectResponse(url=f"/?error=Internal Server Error. Reference ID: {uuid.uuid4()}", status_code=303)
    return HTMLResponse(content="<h1>An internal error occurred. Please contact support.</h1>", status_code=500)

# Include Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(resources.router)
app.include_router(bookings.router)
app.include_router(leaves.router)