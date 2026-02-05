"""Submissions API endpoints."""

import uuid
from datetime import datetime
from typing import List
from io import BytesIO

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.storage import get_storage_client, StorageClient
from app.models.submission import Submission
from app.schemas.submission import SubmissionResponse, SubmissionListResponse
from app.ml.classifier import get_classifier
from app.config import get_settings


router = APIRouter()
settings = get_settings()


async def classify_submission_background(submission_id: uuid.UUID):
    """
    Background task to classify a photo submission.
    
    Args:
        submission_id: ID of the submission to classify
    """
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Get submission
            result = await db.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalar_one_or_none()
            
            if not submission:
                print(f"Submission {submission_id} not found")
                return
            
            # Update status to processing
            submission.classification_status = "processing"
            await db.commit()
            
            # Download photo from storage
            storage = get_storage_client()
            photo_bytes = storage.download_file(submission.photo_path)
            
            # Classify image
            classifier = get_classifier()
            predictions = classifier.classify(photo_bytes)
            
            # Update submission with results
            submission.classification_results = predictions
            submission.classification_status = "completed"
            submission.classified_at = datetime.utcnow()
            submission.classification_error = None
            
            await db.commit()
            print(f"Successfully classified submission {submission_id}")
            
        except Exception as e:
            # Update submission with error
            print(f"Error classifying submission {submission_id}: {str(e)}")
            submission.classification_status = "failed"
            submission.classification_error = str(e)
            await db.commit()


@router.post("/upload", response_model=SubmissionResponse, status_code=201)
async def upload_photo(
    background_tasks: BackgroundTasks,
    name: str = Form(..., min_length=1, max_length=255),
    age: int = Form(..., ge=1, le=150),
    gender: str = Form(..., min_length=1, max_length=50),
    location: str = Form(..., min_length=1, max_length=255),
    country: str = Form(..., min_length=1, max_length=100),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a photo for classification.
    
    This endpoint accepts a photo along with submitter information,
    stores the photo in MinIO, and triggers background classification.
    
    **Parameters:**
    - **name**: Submitter's full name
    - **age**: Submitter's age (1-150)
    - **gender**: Submitter's gender
    - **location**: City or location
    - **country**: Country name
    - **photo**: Image file (JPG, PNG, GIF, WEBP)
    
    **Returns:**
    - Submission object with status "pending"
    - Classification will be performed in the background
    """
    # Validate file type
    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Extract file extension
    file_ext = photo.filename.split(".")[-1].lower() if "." in photo.filename else ""
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {settings.allowed_extensions}"
        )
    
    # Read file
    file_content = await photo.read()
    file_size = len(file_content)
    
    # Validate file size
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    # Generate unique filename
    submission_id = uuid.uuid4()
    photo_path = f"photos/{submission_id}/{photo.filename}"
    
    # Upload to MinIO
    storage = get_storage_client()
    try:
        storage.upload_file(
            file_data=BytesIO(file_content),
            object_name=photo_path,
            content_type=photo.content_type,
            file_size=file_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")
    
    # Create submission record
    # TODO: Get user_id from JWT token (for now using a mock UUID)
    user_id = uuid.uuid4()  # Replace with actual user from JWT
    
    submission = Submission(
        id=submission_id,
        user_id=user_id,
        name=name,
        age=age,
        gender=gender,
        location=location,
        country=country,
        photo_filename=photo.filename,
        photo_path=photo_path,
        photo_size=file_size,
        photo_mime_type=photo.content_type,
        classification_status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_deleted=False
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    # Trigger background classification
    background_tasks.add_task(classify_submission_background, submission_id)
    
    return submission


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific submission by ID.
    
    Returns the submission details including classification results if available.
    """
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.is_deleted == False
        )
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.get("/", response_model=SubmissionListResponse)
async def list_submissions(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all submissions with pagination.
    
    **Parameters:**
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status**: Filter by classification status (pending, processing, completed, failed)
    
    **Returns:**
    - Paginated list of submissions
    """
    # Validate pagination
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    # Build query
    query = select(Submission).where(Submission.is_deleted == False)
    
    if status:
        query = query.where(Submission.classification_status == status)
    
    query = query.order_by(Submission.created_at.desc())
    
    # Get total count
    count_query = select(func.count()).select_from(Submission).where(Submission.is_deleted == False)
    if status:
        count_query = count_query.where(Submission.classification_status == status)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return SubmissionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        submissions=submissions
    )


@router.delete("/{submission_id}", status_code=204)
async def delete_submission(
    submission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a submission.
    
    Marks the submission as deleted without removing it from the database.
    """
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id,
            Submission.is_deleted == False
        )
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.is_deleted = True
    submission.updated_at = datetime.utcnow()
    await db.commit()
    
    return None
