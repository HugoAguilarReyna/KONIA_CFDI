from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from ..core.auth import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from ..core.database import get_database

router = APIRouter()

# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str
    company_id: str
    active_modules: list[str]

class LoginRequest(BaseModel):
    username: str
    password: str
    company_id: str

# Config from env
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Should be imported from config
REFRESH_TOKEN_EXPIRE_MINUTES = 720

# Helper to map string tenant IDs to integer company IDs for fiscal_reports
def get_database_company_id(tenant_id: str) -> int:
    # Manual mapping for Phase 1
    mapping = {
        "TENANT_001": 2
    }
    # Default to 0 if not found (will result in empty queries)
    return mapping.get(tenant_id, 0)

@router.post("/login")
async def login_for_access_token(response: Response, form_data: LoginRequest):
    db = get_database()
    users_collection = db["users"]
    
    # 1. Find user by username AND company_id
    user = users_collection.find_one({
        "username": form_data.username, 
        "company_id": form_data.company_id
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, company ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verify Password (SHA-256 custom logic)
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, company ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate Tokens
    # Map string tenant_id to int company_id for database queries
    db_company_id = get_database_company_id(user["company_id"])
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user["username"], 
            "role": user["role"], 
            "company_id": db_company_id, # Int for fiscal_reports
            "tenant_id": user["company_id"] # String for reference
        },
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user["username"], "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    # 4. Set HttpOnly Cookies
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False # Set to True in Production with HTTPS
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False 
    )
    
    return {"message": "Login successful", "user": {
        "username": user["username"],
        "role": user["role"],
        "company_id": user["company_id"],
        "db_company_id": db_company_id,
        "active_modules": user.get("active_modules", [])
    }}

@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Find user to get current roles/company
    db = get_database()
    user = db["users"].find_one({"username": payload.get("sub")})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Issue new access token
    db_company_id = get_database_company_id(user["company_id"])
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={
            "sub": user["username"], 
            "role": user["role"], 
            "company_id": db_company_id,
            "tenant_id": user["company_id"]
        },
        expires_delta=access_token_expires
    )
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    
    return {"message": "Token refreshed"}

@router.get("/me")
async def read_users_me(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Remove 'Bearer ' prefix
    token = token.replace("Bearer ", "")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "company_id": payload.get("company_id")
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
