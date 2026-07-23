from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.services.auth_service import AuthService
from backend.shared.response import success_response, error_response, APIResponse

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "recruiter"
    name: str = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str
    role: Optional[str] = "recruiter"

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=APIResponse)
async def register(req: RegisterRequest):
    service = AuthService()
    user = await service.register_user(req.email, req.password, req.role, req.name)
    return success_response(user, "User registered successfully")

@router.post("/login", response_model=APIResponse)
async def login(req: LoginRequest):
    service = AuthService()
    tokens = await service.login(req.email, req.password)
    return success_response(tokens, "Login successful")

@router.post("/google", response_model=APIResponse)
async def google_auth(req: GoogleAuthRequest):
    """
    Authenticate user using Firebase Auth Google OAuth ID Token.
    Verifies token signature using Firebase Admin SDK and syncs user to Firestore.
    """
    service = AuthService()
    try:
        auth_data = await service.verify_google_oauth_token(req.id_token, req.role or "recruiter")
        return success_response(auth_data, "Google authentication successful")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

@router.post("/verify-token", response_model=APIResponse)
async def verify_token(req: GoogleAuthRequest):
    service = AuthService()
    try:
        auth_data = await service.verify_google_oauth_token(req.id_token, req.role or "recruiter")
        return success_response(auth_data, "Token verified successfully")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

@router.get("/me", response_model=APIResponse)
async def get_me(user_id: str = "current_user_id"):
    service = AuthService()
    profile = await service.get_profile(user_id)
    return success_response(profile)

@router.post("/refresh", response_model=APIResponse)
async def refresh_token(req: RefreshRequest):
    service = AuthService()
    tokens = await service.refresh(req.refresh_token)
    return success_response(tokens)
