"""Submission repository for database operations."""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission


class SubmissionRepository:
    """
    Repository for Submission database operations.

    Implements Repository pattern to separate data access from business logic.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create(self, submission: Submission) -> Submission:
        """
        Persist a new submission.

        Args:
            submission: Submission model instance

        Returns:
            Created submission with refreshed fields
        """
        self.db.add(submission)
        await self.db.flush()
        await self.db.refresh(submission)
        return submission

    async def get_by_id(
        self, submission_id: UUID, include_deleted: bool = False
    ) -> Optional[Submission]:
        """
        Get submission by ID.

        Args:
            submission_id: Submission UUID
            include_deleted: Whether to include soft-deleted records

        Returns:
            Submission if found, None otherwise
        """
        query = select(Submission).where(Submission.id == submission_id)
        if not include_deleted:
            query = query.where(Submission.is_deleted.is_(False))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Submission], int]:
        """
        List submissions for a specific user with pagination.

        Args:
            user_id: User UUID
            status: Optional classification status filter
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (submissions list, total count)
        """
        base_filter = [
            Submission.user_id == user_id,
            Submission.is_deleted.is_(False),
        ]
        if status:
            base_filter.append(Submission.classification_status == status)

        # Count
        count_query = (
            select(func.count())
            .select_from(Submission)
            .where(*base_filter)
        )
        total = (await self.db.execute(count_query)).scalar()

        # Data
        offset = (page - 1) * page_size
        data_query = (
            select(Submission)
            .where(*base_filter)
            .order_by(Submission.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(data_query)
        submissions = result.scalars().all()

        return submissions, total

    async def soft_delete(self, submission_id: UUID, user_id: UUID) -> bool:
        """
        Soft-delete a submission owned by a specific user.

        Args:
            submission_id: Submission UUID
            user_id: Owner user UUID

        Returns:
            True if deleted, False if not found or not owned
        """
        result = await self.db.execute(
            select(Submission).where(
                Submission.id == submission_id,
                Submission.user_id == user_id,
                Submission.is_deleted.is_(False),
            )
        )
        submission = result.scalar_one_or_none()

        if not submission:
            return False

        submission.is_deleted = True
        submission.updated_at = datetime.now(timezone.utc)
        return True
