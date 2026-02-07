"""Refresh token repository for database operations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import RefreshToken


class TokenRepository:
    """
    Repository for RefreshToken database operations.
    
    Manages refresh token storage, retrieval, and revocation.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime
    ) -> RefreshToken:
        """
        Create a new refresh token.
        
        Args:
            user_id: User UUID
            token: Hashed refresh token
            expires_at: Token expiration timestamp
        
        Returns:
            Created refresh token
        
        Example:
            >>> token = await token_repo.create(
            ...     user_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            ...     token="hashed_token",
            ...     expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            ... )
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)
        
        return refresh_token
    
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """
        Get refresh token by token string.
        
        Args:
            token: Token string to search for
        
        Returns:
            RefreshToken if found, None otherwise
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """
        Get all refresh tokens for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            List of refresh tokens
        """
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def revoke(self, token: str) -> bool:
        """
        Revoke a refresh token.
        
        Args:
            token: Token string to revoke
        
        Returns:
            True if token was revoked, False if not found
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        
        return result.rowcount > 0
    
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of tokens revoked
        """
        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked == False)
            .values(revoked=True)
        )
        
        return result.rowcount
    
    async def delete_expired(self) -> int:
        """
        Delete expired refresh tokens.
        
        Returns:
            Number of tokens deleted
        """
        result = await self.db.execute(
            delete(RefreshToken)
            .where(RefreshToken.expires_at < datetime.now(timezone.utc))
        )
        
        return result.rowcount
    
    async def delete_by_user_id(self, user_id: UUID) -> int:
        """
        Delete all refresh tokens for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of tokens deleted
        """
        result = await self.db.execute(
            delete(RefreshToken)
            .where(RefreshToken.user_id == user_id)
        )
        
        return result.rowcount
