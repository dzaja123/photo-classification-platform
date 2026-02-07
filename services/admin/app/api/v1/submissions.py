"""Admin submissions endpoints with filtering."""

import math
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy import select, func, and_, or_, desc, asc, case
from sqlalchemy.sql import Select

from app.api.dependencies import get_current_admin
from app.core.database import get_db
from app.models.submission import Submission
from app.schemas.submission import SubmissionResponse, SubmissionListResponse
from app.schemas.analytics import AnalyticsResponse, AgeDistribution


router = APIRouter()


def build_filters_query(
    query: Select,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    gender: Optional[List[str]] = None,
    country: Optional[List[str]] = None,
    location: Optional[str] = None,
    classification_status: Optional[str] = None,
    classification_result: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
) -> Select:
    """
    Build SQLAlchemy query with filters.

    Args:
        query: Base query
        age_min: Minimum age
        age_max: Maximum age
        gender: List of genders
        country: List of countries
        location: Location (partial match)
        classification_status: Classification status
        classification_result: Classification result
        date_from: Start date
        date_to: End date
        search: Search term

    Returns:
        Filtered query
    """
    conditions = [Submission.is_deleted.is_(False)]

    # Age filters
    if age_min is not None:
        conditions.append(Submission.age >= age_min)
    if age_max is not None:
        conditions.append(Submission.age <= age_max)

    # Gender filter
    if gender:
        conditions.append(Submission.gender.in_(gender))

    # Country filter
    if country:
        conditions.append(Submission.country.in_(country))

    # Location filter (partial match)
    if location:
        conditions.append(Submission.location.ilike(f"%{location}%"))

    # Classification filters
    if classification_status:
        conditions.append(Submission.classification_status == classification_status)

    if classification_result:
        # Search in JSON classification_results
        conditions.append(
            func.jsonb_path_exists(
                Submission.classification_results,
                f'$[*] ? (@.class == "{classification_result}")',
            )
        )

    # Date filters
    if date_from:
        conditions.append(Submission.created_at >= date_from)
    if date_to:
        conditions.append(Submission.created_at <= date_to)

    # Search filter (name or location)
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Submission.name.ilike(search_term),
                Submission.location.ilike(search_term),
                Submission.country.ilike(search_term),
            )
        )

    return query.where(and_(*conditions))


@router.get("/submissions", response_model=SubmissionListResponse)
async def list_submissions(
    # Age filters
    age_min: Optional[int] = Query(None, ge=1, le=150, description="Minimum age"),
    age_max: Optional[int] = Query(None, ge=1, le=150, description="Maximum age"),
    # Gender filter
    gender: Optional[List[str]] = Query(
        None, description="Filter by gender (can specify multiple)"
    ),
    # Location filters
    country: Optional[List[str]] = Query(
        None, description="Filter by country (can specify multiple)"
    ),
    location: Optional[str] = Query(
        None, description="Filter by location (partial match)"
    ),
    # Classification filters
    classification_status: Optional[str] = Query(
        None, description="Filter by status (pending/processing/completed/failed)"
    ),
    classification_result: Optional[str] = Query(
        None, description="Filter by classification result"
    ),
    # Date filters
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    # Search
    search: Optional[str] = Query(
        None, description="Search in name, location, country"
    ),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    # Sorting
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """
    List all submissions with advanced filtering.

    **Admin only endpoint** - requires admin role.

    Supports filtering by:
    - Age range (min/max)
    - Gender (multiple)
    - Country (multiple)
    - Location (partial match)
    - Classification status
    - Classification result
    - Date range
    - Search term

    Results are paginated and sortable.
    """
    # Build base query
    query = select(Submission)

    # Apply filters
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

    # Get total count
    count_query = select(func.count()).select_from(Submission)
    count_query = build_filters_query(
        count_query,
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

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply sorting
    sort_column = getattr(Submission, sort_by, Submission.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await db.execute(query)
    submissions = result.scalars().all()

    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Build filters applied dict
    filters_applied = {}
    if age_min is not None:
        filters_applied["age_min"] = age_min
    if age_max is not None:
        filters_applied["age_max"] = age_max
    if gender:
        filters_applied["gender"] = gender
    if country:
        filters_applied["country"] = country
    if location:
        filters_applied["location"] = location
    if classification_status:
        filters_applied["classification_status"] = classification_status
    if classification_result:
        filters_applied["classification_result"] = classification_result
    if date_from:
        filters_applied["date_from"] = date_from.isoformat()
    if date_to:
        filters_applied["date_to"] = date_to.isoformat()
    if search:
        filters_applied["search"] = search

    return SubmissionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        submissions=submissions,
        filters_applied=filters_applied if filters_applied else None,
    )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """
    Get a specific submission by ID.

    **Admin only endpoint** - requires admin role.
    """
    result = await db.execute(
        select(Submission).where(
            Submission.id == submission_id, Submission.is_deleted.is_(False)
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    """
    Get analytics dashboard data.

    **Admin only endpoint** - requires admin role.

    Returns aggregated statistics:
    - Total submissions and users
    - Submissions by time period
    - Distribution by gender, country, classification
    - Age distribution
    - Average confidence
    """
    # Get current time
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    # Total submissions
    total_submissions_result = await db.execute(
        select(func.count())
        .select_from(Submission)
        .where(Submission.is_deleted.is_(False))
    )
    total_submissions = total_submissions_result.scalar()

    # Total unique users
    total_users_result = await db.execute(
        select(func.count(func.distinct(Submission.user_id)))
        .select_from(Submission)
        .where(Submission.is_deleted.is_(False))
    )
    total_users = total_users_result.scalar()

    # Submissions today
    submissions_today_result = await db.execute(
        select(func.count())
        .select_from(Submission)
        .where(
            and_(Submission.is_deleted.is_(False), Submission.created_at >= today_start)
        )
    )
    submissions_today = submissions_today_result.scalar()

    # Submissions this week
    submissions_week_result = await db.execute(
        select(func.count())
        .select_from(Submission)
        .where(
            and_(Submission.is_deleted.is_(False), Submission.created_at >= week_start)
        )
    )
    submissions_this_week = submissions_week_result.scalar()

    # Submissions this month
    submissions_month_result = await db.execute(
        select(func.count())
        .select_from(Submission)
        .where(
            and_(Submission.is_deleted.is_(False), Submission.created_at >= month_start)
        )
    )
    submissions_this_month = submissions_month_result.scalar()

    # By gender
    by_gender_result = await db.execute(
        select(Submission.gender, func.count())
        .where(Submission.is_deleted.is_(False))
        .group_by(Submission.gender)
    )
    by_gender = {row[0]: row[1] for row in by_gender_result}

    # By country (top 10)
    by_country_result = await db.execute(
        select(Submission.country, func.count())
        .where(Submission.is_deleted.is_(False))
        .group_by(Submission.country)
        .order_by(desc(func.count()))
        .limit(10)
    )
    by_country = {row[0]: row[1] for row in by_country_result}

    # By classification status
    by_status_result = await db.execute(
        select(Submission.classification_status, func.count())
        .where(Submission.is_deleted.is_(False))
        .group_by(Submission.classification_status)
    )
    by_status = {row[0]: row[1] for row in by_status_result}

    # By classification result (top 10) — extract top-1 class from JSONB
    by_classification = {}
    try:
        top_class_expr = func.jsonb_array_element(
            Submission.classification_results, 0
        ).op("->>")("class")
        by_class_result = await db.execute(
            select(
                top_class_expr.label("top_class"),
                func.count().label("cnt"),
            )
            .where(
                and_(
                    Submission.is_deleted.is_(False),
                    Submission.classification_results.isnot(None),
                )
            )
            .group_by(top_class_expr)
            .order_by(desc("cnt"))
            .limit(10)
        )
        by_classification = {row[0]: row[1] for row in by_class_result if row[0]}
    except Exception:
        await db.rollback()
        by_classification = {}

    # Age distribution
    age_distribution = []
    try:
        age_distribution_result = await db.execute(
            select(
                case(
                    (Submission.age < 18, "Under 18"),
                    (Submission.age <= 25, "18-25"),
                    (Submission.age <= 35, "26-35"),
                    (Submission.age <= 45, "36-45"),
                    (Submission.age <= 55, "46-55"),
                    (Submission.age <= 65, "56-65"),
                    else_="65+",
                ).label("age_range"),
                func.count().label("count"),
            )
            .where(Submission.is_deleted.is_(False))
            .group_by(sa.text("age_range"))
        )
        age_distribution = [
            AgeDistribution(range=row[0], count=row[1])
            for row in age_distribution_result
        ]
    except Exception:
        await db.rollback()
        age_distribution = []

    # Average confidence from top-1 prediction
    avg_confidence = 0.0
    try:
        conf_expr = func.cast(
            func.jsonb_array_element(Submission.classification_results, 0).op("->>")(
                "confidence"
            ),
            sa.Float,
        )
        avg_conf_result = await db.execute(
            select(func.avg(conf_expr)).where(
                and_(
                    Submission.is_deleted.is_(False),
                    Submission.classification_results.isnot(None),
                )
            )
        )
        val = avg_conf_result.scalar()
        if val is not None:
            avg_confidence = round(float(val), 4)
    except Exception:
        await db.rollback()
        avg_confidence = 0.0

    return AnalyticsResponse(
        total_submissions=total_submissions,
        total_users=total_users,
        submissions_today=submissions_today,
        submissions_this_week=submissions_this_week,
        submissions_this_month=submissions_this_month,
        by_gender=by_gender,
        by_country=by_country,
        by_classification=by_classification,
        by_status=by_status,
        age_distribution=age_distribution,
        avg_confidence=avg_confidence,
    )
