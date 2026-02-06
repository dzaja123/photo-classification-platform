"""Authentication endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_auth_service,
    get_client_ip,
    get_user_agent,
    get_current_user
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest
)
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService
from app.middleware.rate_limit import rate_limit


router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, username, and password"
)
@rate_limit("3/minute", key_prefix="register")
async def register(
    request: Request,
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    ip_address: Optional[str] = Depends(get_client_ip)
):
    """
    Register a new user.
    
    **Requirements:**
    - Email must be valid and unique
    - Username must be 3-30 characters, alphanumeric + underscore, unique
    - Password must be at least 8 characters with uppercase, lowercase, digit, and special character
    
    **Returns:**
    - User profile
    - Access token (15 minutes)
    - Refresh token (7 days)
    """
    user, tokens = await auth_service.register(user_data, ip_address)
    
    return APIResponse(
        success=True,
        message="User registered successfully",
        data={
            "user": user.model_dump(),
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in
        }
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="User login",
    description="Authenticate user with username/email and password"
)
@rate_limit("5/minute", key_prefix="login")
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip_address: Optional[str] = Depends(get_client_ip),
    user_agent: Optional[str] = Depends(get_user_agent)
):
    """
    Login with username/email and password.
    
    **Accepts:**
    - Username or email
    - Password
    
    **Returns:**
    - Access token (15 minutes)
    - Refresh token (7 days)
    
    **Rate Limit:** 5 requests per minute per IP
    """
    tokens = await auth_service.login(
        username=login_data.username,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return APIResponse(
        success=True,
        message="Login successful",
        data=tokens
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ip_address: Optional[str] = Depends(get_client_ip)
):
    """
    Refresh access token.
    
    **Requires:**
    - Valid refresh token
    
    **Returns:**
    - New access token (15 minutes)
    - New refresh token (7 days)
    
    **Note:** Old refresh token will be revoked
    """
    tokens = await auth_service.refresh_tokens(
        refresh_token=refresh_data.refresh_token,
        ip_address=ip_address
    )
    
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data=tokens
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict],
    summary="User logout",
    description="Logout user by revoking tokens"
)
async def logout(
    logout_data: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    ip_address: Optional[str] = Depends(get_client_ip)
):
    """
    Logout user.
    
    **Requires:**
    - Valid access token (in Authorization header)
    - Optional refresh token (in request body)
    
    **Actions:**
    - Blacklists access token
    - Revokes refresh token (if provided)
    """
    access_token = credentials.credentials
    
    await auth_service.logout(
        access_token=access_token,
        refresh_token=logout_data.refresh_token,
        ip_address=ip_address
    )
    
    return APIResponse(
        success=True,
        message="Logout successful",
        data={}
    )


