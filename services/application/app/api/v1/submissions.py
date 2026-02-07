"""Submissions API endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import JWTError

from app.api.dependencies import _decode_token, get_current_user_id
from app.config import get_settings
from app.core.database import AsyncSessionLocal, get_db
from app.core.storage import get_storage_client
from app.ml.classifier import get_classifier
from app.models.submission import Submission
from app.schemas.submission import SubmissionResponse, SubmissionListResponse
from app.services.submission_service import SubmissionService
from shared.enums import SubmissionStatus, TokenType


router = APIRouter()
settings = get_settings()


# ---------------------------------------------------------------------------
# Background classification task
# ---------------------------------------------------------------------------

async def classify_submission_background(submission_id: uuid.UUID) -> None:
    """
    Background task to classify a photo submission.

    Uses its own DB session so the request handler can return immediately.
    Handles failures gracefully by marking the submission as "failed".

    Args:
        submission_id: ID of the submission to classify
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()

            if not submission:
                return

            # Mark as processing
            submission.classification_status = SubmissionStatus.PROCESSING
            await db.commit()

            # Download photo from storage
            storage = get_storage_client()
            photo_bytes = storage.download_file(submission.photo_path)

            # Classify image
            classifier = get_classifier()
            predictions = classifier.classify(photo_bytes)

            # Persist results
            submission.classification_results = predictions
            submission.classification_status = SubmissionStatus.COMPLETED
            submission.classified_at = datetime.now(timezone.utc)
            submission.classification_error = None
            await db.commit()

        except Exception as e:
            await db.rollback()
            # Re-fetch inside a clean transaction to record the error
            try:
                result = await db.execute(
                    select(Submission).where(Submission.id == submission_id)
                )
                submission = result.scalar_one_or_none()
                if submission:
                    submission.classification_status = SubmissionStatus.FAILED
                    submission.classification_error = str(e)
                    await db.commit()
            except Exception:
                await db.rollback()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=SubmissionResponse, status_code=201)
async def upload_photo(
    background_tasks: BackgroundTasks,
    name: str = Form(..., min_length=1, max_length=255),
    age: int = Form(..., ge=1, le=150),
    gender: str = Form(..., min_length=1, max_length=50),
    location: str = Form(..., min_length=1, max_length=255),
    country: str = Form(..., min_length=1, max_length=100),
    description: Optional[str] = Form(None, max_length=500),
    photo: UploadFile = File(...),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a photo for classification.

    Accepts a photo along with submitter information, stores the photo in
    MinIO, and triggers background ML classification.

    **Parameters:**
    - **name**: Submitter's full name
    - **age**: Submitter's age (1-150)
    - **gender**: Submitter's gender
    - **location**: City or location
    - **country**: Country name
    - **description**: Optional description
    - **photo**: Image file (JPG, PNG, GIF, WEBP)

    **Returns:**
    - Submission object with status "pending"
    - Classification will be performed in the background
    """
    service = SubmissionService(db)
    submission = await service.create_submission(
        user_id=user_id,
        name=name,
        age=age,
        gender=gender,
        location=location,
        country=country,
        description=description,
        photo=photo,
    )

    # Trigger background classification
    background_tasks.add_task(classify_submission_background, submission.id)

    return submission


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific submission by ID.

    Returns the submission details including classification results if available.
    Only the owning user can access their submissions.
    """
    service = SubmissionService(db)
    return await service.get_submission(submission_id, user_id)


@router.get("/", response_model=SubmissionListResponse)
async def list_submissions(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    List current user's submissions with pagination.

    **Parameters:**
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by classification status (pending, processing, completed, failed)
    """
    service = SubmissionService(db)
    submissions, total = await service.list_submissions(
        user_id=user_id,
        page=page,
        page_size=page_size,
        status_filter=status,
    )

    return SubmissionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        submissions=submissions,
    )


@router.delete("/{submission_id}", status_code=204)
async def delete_submission(
    submission_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a submission.

    Only the owning user can delete their submissions.
    """
    service = SubmissionService(db)
    await service.delete_submission(submission_id, user_id)
    return None


@router.get("/{submission_id}/photo")
async def get_submission_photo(
    submission_id: uuid.UUID,
    token: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Serve a submission's photo directly.

    Accepts JWT as a `token` query parameter so that `<img src="...">` tags
    can authenticate without setting headers.

    Downloads the image from MinIO and streams it to the client, avoiding
    redirect issues when MinIO is on an internal Docker network.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required",
        )

    try:
        payload = _decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    if payload.get("token_type") != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.is_deleted.is_(False),
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    storage = get_storage_client()
    try:
        photo_bytes = storage.download_file(submission.photo_path)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo file not found in storage",
        )

    return Response(
        content=photo_bytes,
        media_type=submission.photo_mime_type,
        headers={"Cache-Control": "private, max-age=3600"},
    )
