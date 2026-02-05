"""User management endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_auth_service,
    get_current_user,
    get_client_ip
)
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.auth import PasswordChangeRequest
from app.schemas.response import APIResponse
from app.services.auth_service import AuthService


router = APIRouter()


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current user profile",
    description="Get authenticated user's profile information"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    **Requires:**
    - Valid access token
    
    **Returns:**
    - Complete user profile
    """
    user_response = UserResponse.model_validate(current_user)
    
    return APIResponse(
        success=True,
        message="User profile retrieved",
        data=user_response
    )


@router.put(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update current user profile",
    description="Update authenticated user's profile information"
)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user profile.
    
    **Requires:**
    - Valid access token
    
    **Updatable fields:**
    - full_name
    
    **Returns:**
    - Updated user profile
    """
    updated_user = await auth_service.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=updated_user
    )


@router.post(
    "/change-password",
    response_model=APIResponse[dict],
    summary="Change password",
    description="Change authenticated user's password"
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    ip_address: Optional[str] = Depends(get_client_ip)
):
    """
    Change user password.
    
    **Requires:**
    - Valid access token
    - Current password
    - New password (must meet strength requirements)
    
    **Security:**
    - All refresh tokens will be revoked after password change
    - User will need to login again
    
    **Returns:**
    - Success confirmation
    """
    await auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
        ip_address=ip_address
    )
    
    return APIResponse(
        success=True,
        message="Password changed successfully. Please login again.",
        data={}
    )
