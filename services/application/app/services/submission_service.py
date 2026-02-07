"""Submission service with business logic."""

import uuid
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional, List, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.storage import get_storage_client
from app.models.submission import Submission
from app.repositories.submission_repository import SubmissionRepository
from shared.enums import SubmissionStatus


settings = get_settings()


class SubmissionService:
    """
    Submission service handling business logic.

    Manages photo upload, validation, storage, and retrieval.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize submission service.

        Args:
            db: Database session
        """
        self.db = db
        self.repo = SubmissionRepository(db)

    async def create_submission(
        self,
        user_id: uuid.UUID,
        name: str,
        age: int,
        gender: str,
        location: str,
        country: str,
        photo: UploadFile,
        description: Optional[str] = None,
    ) -> Submission:
        """
        Create a new photo submission.

        Validates the file, uploads to MinIO, and creates the DB record.

        Args:
            user_id: Authenticated user UUID
            name: Submitter's name
            age: Submitter's age
            gender: Submitter's gender
            location: City / location
            country: Country
            photo: Uploaded image file
            description: Optional description

        Returns:
            Created Submission

        Raises:
            HTTPException: On validation or storage failure
        """
        # Validate file type
        if not photo.content_type or not photo.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image",
            )

        file_ext = (
            photo.filename.split(".")[-1].lower()
            if photo.filename and "." in photo.filename
            else ""
        )
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {settings.allowed_extensions}",
            )

        # Read and validate size
        file_content = await photo.read()
        file_size = len(file_content)

        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
            )

        # Upload to MinIO
        submission_id = uuid.uuid4()
        photo_path = f"photos/{submission_id}/{photo.filename}"
        storage = get_storage_client()

        try:
            storage.upload_file(
                file_data=BytesIO(file_content),
                object_name=photo_path,
                content_type=photo.content_type,
                file_size=file_size,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo: {str(e)}",
            )

        # Create DB record
        now = datetime.now(timezone.utc)
        submission = Submission(
            id=submission_id,
            user_id=user_id,
            name=name,
            age=age,
            gender=gender,
            location=location,
            country=country,
            description=description,
            photo_filename=photo.filename,
            photo_path=photo_path,
            photo_size=file_size,
            photo_mime_type=photo.content_type,
            classification_status=SubmissionStatus.PENDING.value,
            created_at=now,
            updated_at=now,
            is_deleted=False,
        )

        submission = await self.repo.create(submission)
        return submission

    async def get_submission(
        self, submission_id: uuid.UUID, user_id: uuid.UUID
    ) -> Submission:
        """
        Get a submission owned by the given user.

        Args:
            submission_id: Submission UUID
            user_id: Owner user UUID

        Returns:
            Submission

        Raises:
            HTTPException: If not found or not owned by user
        """
        submission = await self.repo.get_by_id(submission_id)

        if not submission or submission.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )

        return submission

    async def list_submissions(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
    ) -> Tuple[List[Submission], int]:
        """
        List submissions for a user with pagination.

        Args:
            user_id: User UUID
            page: Page number
            page_size: Items per page
            status_filter: Optional classification status filter

        Returns:
            Tuple of (submissions, total_count)
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        return await self.repo.list_by_user(
            user_id=user_id,
            status=status_filter,
            page=page,
            page_size=page_size,
        )

    async def delete_submission(
        self, submission_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """
        Soft-delete a submission owned by the given user.

        Args:
            submission_id: Submission UUID
            user_id: Owner user UUID

        Raises:
            HTTPException: If not found or not owned by user
        """
        deleted = await self.repo.soft_delete(submission_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found",
            )
