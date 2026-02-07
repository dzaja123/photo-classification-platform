"""Data export endpoints."""

import csv
import json
from io import StringIO
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.dependencies import get_current_admin
from app.core.database import get_db
from app.models.submission import Submission
from app.api.v1.submissions import build_filters_query
from app.config import get_settings


router = APIRouter()
settings = get_settings()


@router.get("/export/submissions/csv")
async def export_submissions_csv(
    # Filters (same as list endpoint)
    age_min: Optional[int] = Query(None, ge=1, le=150),
    age_max: Optional[int] = Query(None, ge=1, le=150),
    gender: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    location: Optional[str] = Query(None),
    classification_status: Optional[str] = Query(None),
    classification_result: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records to export"),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """
    Export submissions to CSV format.

    **Admin only endpoint** - requires admin role.

    Applies the same filters as the list endpoint.
    Maximum 10,000 records per export.

    Returns CSV file for download.
    """
    # Build query with filters
    query = select(Submission)
    query = build_filters_query(
        query,
        age_min=age_min,
        age_max=age_max,
        gender=gender,
        country=country,
        location=location,
        classification_status=classification_status,
        classification_result=classification_result,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    # Limit results
    query = query.limit(min(limit, settings.export_max_records))

    # Execute query
    result = await db.execute(query)
    submissions = result.scalars().all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(
        [
            "ID",
            "User ID",
            "Name",
            "Age",
            "Gender",
            "Location",
            "Country",
            "Description",
            "Photo Filename",
            "Photo Size (bytes)",
            "Classification Status",
            "Classification Result",
            "Classification Confidence",
            "Created At",
            "Classified At",
        ]
    )

    # Write data
    for sub in submissions:
        # Extract top classification result
        classification_class = ""
        classification_conf = ""
        if sub.classification_results and len(sub.classification_results) > 0:
            classification_class = sub.classification_results[0].get("class", "")
            classification_conf = sub.classification_results[0].get("confidence", "")

        writer.writerow(
            [
                str(sub.id),
                str(sub.user_id),
                sub.name,
                sub.age,
                sub.gender,
                sub.location,
                sub.country,
                sub.description or "",
                sub.photo_filename,
                sub.photo_size,
                sub.classification_status,
                classification_class,
                classification_conf,
                sub.created_at.isoformat() if sub.created_at else "",
                sub.classified_at.isoformat() if sub.classified_at else "",
            ]
        )

    # Return CSV file
    csv_content = output.getvalue()
    filename = (
        f"submissions_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/submissions/json")
async def export_submissions_json(
    # Filters (same as list endpoint)
    age_min: Optional[int] = Query(None, ge=1, le=150),
    age_max: Optional[int] = Query(None, ge=1, le=150),
    gender: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    location: Optional[str] = Query(None),
    classification_status: Optional[str] = Query(None),
    classification_result: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum records to export"),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """
    Export submissions to JSON format.

    **Admin only endpoint** - requires admin role.

    Applies the same filters as the list endpoint.
    Maximum 10,000 records per export.

    Returns JSON file for download.
    """
    # Build query with filters
    query = select(Submission)
    query = build_filters_query(
        query,
        age_min=age_min,
        age_max=age_max,
        gender=gender,
        country=country,
        location=location,
        classification_status=classification_status,
        classification_result=classification_result,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    # Limit results
    query = query.limit(min(limit, settings.export_max_records))

    # Execute query
    result = await db.execute(query)
    submissions = result.scalars().all()

    # Convert to JSON-serializable format
    data = []
    for sub in submissions:
        data.append(
            {
                "id": str(sub.id),
                "user_id": str(sub.user_id),
                "name": sub.name,
                "age": sub.age,
                "gender": sub.gender,
                "location": sub.location,
                "country": sub.country,
                "description": sub.description,
                "photo_filename": sub.photo_filename,
                "photo_path": sub.photo_path,
                "photo_size": sub.photo_size,
                "photo_mime_type": sub.photo_mime_type,
                "classification_status": sub.classification_status,
                "classification_results": sub.classification_results,
                "classification_error": sub.classification_error,
                "classified_at": sub.classified_at.isoformat()
                if sub.classified_at
                else None,
                "created_at": sub.created_at.isoformat() if sub.created_at else None,
                "updated_at": sub.updated_at.isoformat() if sub.updated_at else None,
            }
        )

    # Create JSON
    json_content = json.dumps(
        {
            "export_date": datetime.now(timezone.utc).isoformat(),
            "total_records": len(data),
            "filters_applied": {
                "age_min": age_min,
                "age_max": age_max,
                "gender": gender,
                "country": country,
                "location": location,
                "classification_status": classification_status,
                "classification_result": classification_result,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "search": search,
            },
            "submissions": data,
        },
        indent=2,
    )

    filename = f"submissions_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
