"""Authentication service with business logic."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_token_jti,
    get_token_expiration
)
from app.core.cache import blacklist_token, is_token_blacklisted
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.auth import TokenResponse
from shared.audit_logger import AuditLogger
from shared.enums import AuditEventType, AuditEventStatus, TokenType


settings = get_settings()


class AuthService:
    """
    Authentication service handling business logic.
    
    Manages user registration, login, token refresh, and logout.
    Integrates with repositories and audit logging.
    """
    
    def __init__(
        self,
        db: AsyncSession,
        audit_logger: Optional[AuditLogger] = None
    ):
        """
        Initialize auth service.
        
        Args:
            db: Database session
            audit_logger: Audit logger instance (optional)
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.audit_logger = audit_logger
    
    async def register(
        self,
        user_data: UserCreate,
        ip_address: Optional[str] = None
    ) -> Tuple[UserResponse, TokenResponse]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            ip_address: Client IP address (for audit logging)
        
        Returns:
            Tuple of (UserResponse, TokenResponse)
        
        Raises:
            HTTPException: If email or username already exists
        
        Example:
            >>> user, tokens = await auth_service.register(
            ...     UserCreate(
            ...         email="john@example.com",
            ...         username="johndoe",
            ...         password="SecurePass123!"
            ...     )
            ... )
        """
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            # Audit failed registration attempt
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTH_REGISTER,
                    action="registration_failed",
                    ip_address=ip_address,
                    metadata={"reason": "email_exists", "email": user_data.email},
                    status=AuditEventStatus.FAILURE
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            # Audit failed registration attempt
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTH_REGISTER,
                    action="registration_failed",
                    ip_address=ip_address,
                    metadata={"reason": "username_exists", "username": user_data.username},
                    status=AuditEventStatus.FAILURE
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        try:
            user = await self.user_repo.create(user_data)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        refresh_token = create_refresh_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        # Store refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        await self.token_repo.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        await self.db.commit()
        
        # Audit successful registration
        if self.audit_logger:
            await self.audit_logger.log_event(
                event_type=AuditEventType.AUTH_REGISTER,
                user_id=str(user.id),
                username=user.username,
                action="registration_success",
                ip_address=ip_address,
                metadata={"email": user.email}
            )
        
        # Prepare response
        user_response = UserResponse.model_validate(user)
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
        return user_response, token_response
    
    async def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Authenticate user and generate tokens.
        
        Args:
            username: Username or email
            password: Plain text password
            ip_address: Client IP address (for audit logging)
            user_agent: User agent string (for audit logging)
        
        Returns:
            TokenResponse with access and refresh tokens
        
        Raises:
            HTTPException: If credentials are invalid or account is inactive
        
        Example:
            >>> tokens = await auth_service.login(
            ...     username="johndoe",
            ...     password="SecurePass123!"
            ... )
        """
        # Try to find user by username or email
        user = await self.user_repo.get_by_username(username)
        if not user:
            user = await self.user_repo.get_by_email(username)
        
        # Check if user exists and password is correct
        if not user or not verify_password(password, user.hashed_password):
            # Audit failed login attempt
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTH_FAILED_LOGIN,
                    action="login_failed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata={"username": username, "reason": "invalid_credentials"},
                    status=AuditEventStatus.FAILURE
                )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if account is active
        if not user.is_active:
            # Audit failed login attempt
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTH_FAILED_LOGIN,
                    user_id=str(user.id),
                    username=user.username,
                    action="login_failed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata={"reason": "account_inactive"},
                    status=AuditEventStatus.FAILURE
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Update last login timestamp
        await self.user_repo.update_last_login(user.id)
        
        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        refresh_token = create_refresh_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        # Store refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        await self.token_repo.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at
        )
        
        await self.db.commit()
        
        # Audit successful login
        if self.audit_logger:
            await self.audit_logger.log_event(
                event_type=AuditEventType.AUTH_LOGIN,
                user_id=str(user.id),
                username=user.username,
                action="login_success",
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            ip_address: Client IP address (for audit logging)
        
        Returns:
            TokenResponse with new access and refresh tokens
        
        Raises:
            HTTPException: If refresh token is invalid or revoked
        
        Example:
            >>> tokens = await auth_service.refresh_tokens(
            ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            ... )
        """
        # Decode and verify token
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check token type
        if payload.get("token_type") != TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and await is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Check if token exists in database
        token_record = await self.token_repo.get_by_token(refresh_token)
        if not token_record or token_record.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or revoked"
            )
        
        # Get user
        user_id = UUID(payload.get("sub"))
        user = await self.user_repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Revoke old refresh token
        await self.token_repo.revoke(refresh_token)
        
        # Generate new tokens
        new_access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        new_refresh_token = create_refresh_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )
        
        # Store new refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
        await self.token_repo.create(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=expires_at
        )
        
        await self.db.commit()
        
        # Audit token refresh
        if self.audit_logger:
            await self.audit_logger.log_event(
                event_type=AuditEventType.AUTH_TOKEN_REFRESH,
                user_id=str(user.id),
                username=user.username,
                action="token_refresh_success",
                ip_address=ip_address
            )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    async def logout(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Logout user by blacklisting tokens.
        
        Args:
            access_token: JWT access token to blacklist
            refresh_token: JWT refresh token to revoke (optional)
            ip_address: Client IP address (for audit logging)
        
        Returns:
            True if successful
        
        Example:
            >>> await auth_service.logout(
            ...     access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            ...     refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            ... )
        """
        # Decode access token to get user info
        try:
            payload = decode_token(access_token)
            user_id = payload.get("sub")
            username = payload.get("username")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
        
        # Blacklist access token
        access_jti = get_token_jti(access_token)
        if access_jti:
            access_exp = get_token_expiration(access_token)
            if access_exp:
                ttl = int((access_exp - datetime.now(timezone.utc)).total_seconds())
                if ttl > 0:
                    await blacklist_token(access_jti, ttl)
        
        # Revoke refresh token if provided
        if refresh_token:
            await self.token_repo.revoke(refresh_token)
            
            # Blacklist refresh token
            refresh_jti = get_token_jti(refresh_token)
            if refresh_jti:
                refresh_exp = get_token_expiration(refresh_token)
                if refresh_exp:
                    ttl = int((refresh_exp - datetime.now(timezone.utc)).total_seconds())
                    if ttl > 0:
                        await blacklist_token(refresh_jti, ttl)
        
        await self.db.commit()
        
        # Audit logout
        if self.audit_logger:
            await self.audit_logger.log_event(
                event_type=AuditEventType.AUTH_LOGOUT,
                user_id=user_id,
                username=username,
                action="logout_success",
                ip_address=ip_address
            )
        
        return True
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
        
        Returns:
            User if found, None otherwise
        """
        return await self.user_repo.get_by_id(user_id)
    
    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            user_data: Update data
        
        Returns:
            Updated user response
        """
        user = await self.user_repo.update(user_id, user_data)
        if not user:
            return None
        
        await self.db.commit()
        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User UUID
            current_password: Current password
            new_password: New password
            ip_address: Client IP address (for audit logging)
        
        Returns:
            True if successful
        
        Raises:
            HTTPException: If current password is incorrect
        """
        # Get user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            # Audit failed password change
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=AuditEventType.AUTH_PASSWORD_CHANGE,
                    user_id=str(user.id),
                    username=user.username,
                    action="password_change_failed",
                    ip_address=ip_address,
                    metadata={"reason": "incorrect_current_password"},
                    status=AuditEventStatus.FAILURE
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Change password
        await self.user_repo.change_password(user_id, new_password)
        
        # Revoke all refresh tokens for security
        await self.token_repo.revoke_all_for_user(user_id)
        
        await self.db.commit()
        
        # Audit successful password change
        if self.audit_logger:
            await self.audit_logger.log_event(
                event_type=AuditEventType.AUTH_PASSWORD_CHANGE,
                user_id=str(user.id),
                username=user.username,
                action="password_change_success",
                ip_address=ip_address
            )
        
        return True
