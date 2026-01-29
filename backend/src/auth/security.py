from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
import hashlib

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_unsafe_key_for_dev")
ALGORITHM = "HS256"
# Parse expire minutes, default to 30 if missing/invalid
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # 1. Try checking the SHA256 pre-hashed version (New System)
    # This prevents the 72-byte limit error for long passwords
    sha256_password = hashlib.sha256(plain_password.encode()).hexdigest()
    try:
        if pwd_context.verify(sha256_password, hashed_password):
            return True
    except Exception:
        pass
        
    # 2. Fallback: Check raw password (Legacy System)
    # Only try this if password is short enough to not crash bcrypt
    if len(plain_password.encode()) <= 72:
        return pwd_context.verify(plain_password, hashed_password)
        
    return False

def get_password_hash(password):
    # Always pre-hash using SHA256 to allow infinite length passwords
    # and produce a safe 64-byte input for bcrypt
    sha256_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha256_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Decodes the token and returns the payload (claims).
    Returns None if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
