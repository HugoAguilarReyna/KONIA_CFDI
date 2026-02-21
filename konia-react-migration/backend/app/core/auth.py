from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 720))

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# --- Password Hashing (Legacy Compatibility) ---
# Original app used SHA-256 directly. Here we adapt to a robust context but kept compatible if needed.
# For migration, we will use passlib's sha256_crypt which is standard. 
# IF the original app used raw SHA256(salt + password), we might need a custom verifier.
# Checking create_admin.py from context:
# salted_pass = password + SECRET_KEY
# return hashlib.sha256(salted_pass.encode()).hexdigest()

import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against the custom SHA-256 hash used in the legacy system."""
    # We must use the SAME logic as the legacy app
    salted_pass = plain_password + SECRET_KEY
    computed_hash = hashlib.sha256(salted_pass.encode()).hexdigest()
    return computed_hash == hashed_password

def get_password_hash(password: str) -> str:
    """Hashes a password using the custom SHA-256 logic."""
    salted_pass = password + SECRET_KEY
    return hashlib.sha256(salted_pass.encode()).hexdigest()

# --- JWT Logic ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
