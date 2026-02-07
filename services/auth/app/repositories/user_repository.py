"""User repository for database operations."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from shared.enums import UserRole


class UserRepository:
    """
    Repository for User database operations.

    Implements Repository pattern to separate data access from business logic.
    All database operations are async for performance.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            IntegrityError: If email or username already exists

        Example:
            >>> user = await user_repo.create(UserCreate(
            ...     email="john@example.com",
            ...     username="johndoe",
            ...     password="SecurePass123!"
            ... ))
        """
        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user instance
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.USER,  # Default role
            is_active=True,
            is_verified=False,
        )

        # Add to session
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def update(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """
        Update user profile.

        Args:
            user_id: User UUID
            user_data: Update data

        Returns:
            Updated user if found, None otherwise
        """
        # Build update dict (only non-None values)
        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_by_id(user_id)

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now(timezone.utc)

        # Execute update
        await self.db.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )

        # Return updated user
        return await self.get_by_id(user_id)

    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp.

        Args:
            user_id: User UUID
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )

    async def deactivate(self, user_id: UUID) -> Optional[User]:
        """
        Deactivate user account (soft delete).

        Args:
            user_id: User UUID

        Returns:
            Deactivated user if found, None otherwise
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )

        return await self.get_by_id(user_id)

    async def activate(self, user_id: UUID) -> Optional[User]:
        """
        Activate user account.

        Args:
            user_id: User UUID

        Returns:
            Activated user if found, None otherwise
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=True, updated_at=datetime.now(timezone.utc))
        )

        return await self.get_by_id(user_id)

    async def verify_email(self, user_id: UUID) -> Optional[User]:
        """
        Mark user email as verified.

        Args:
            user_id: User UUID

        Returns:
            Verified user if found, None otherwise
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_verified=True, updated_at=datetime.now(timezone.utc))
        )

        return await self.get_by_id(user_id)

    async def change_password(self, user_id: UUID, new_password: str) -> Optional[User]:
        """
        Change user password.

        Args:
            user_id: User UUID
            new_password: New plain text password (will be hashed)

        Returns:
            Updated user if found, None otherwise
        """
        hashed_password = hash_password(new_password)

        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                hashed_password=hashed_password, updated_at=datetime.now(timezone.utc)
            )
        )

        return await self.get_by_id(user_id)

    async def change_role(self, user_id: UUID, new_role: UserRole) -> Optional[User]:
        """
        Change user role (admin only).

        Args:
            user_id: User UUID
            new_role: New role

        Returns:
            Updated user if found, None otherwise
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(role=new_role, updated_at=datetime.now(timezone.utc))
        )

        return await self.get_by_id(user_id)
