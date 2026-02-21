import math
from pathlib import Path
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date

from ..database import get_db
from ..models import DetectionRecord
from ..schemas import HistoryResponse, DetectionResponse

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    min_detections: int | None = Query(None),
    max_detections: int | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Lấy lịch sử detection với filter và phân trang.

    Filters:
    - search: tìm theo original_filename (ILIKE)
    - date_from / date_to: lọc theo khoảng ngày
    - min/max_detections: lọc theo số người detect được
    """
    # ── Build query ──
    query = db.query(DetectionRecord)

    # Search by filename
    if search:
        query = query.filter(
            DetectionRecord.original_filename.ilike(f"%{search}%")
        )

    # Filter by date range
    if date_from:
        query = query.filter(DetectionRecord.created_at >= date_from)
    if date_to:
        from datetime import datetime
        date_to_end = datetime.combine(date_to, datetime.max.time())
        query = query.filter(DetectionRecord.created_at <= date_to_end)

    # Filter by detection count
    if min_detections is not None:
        query = query.filter(DetectionRecord.num_detections >= min_detections)
    if max_detections is not None:
        query = query.filter(DetectionRecord.num_detections <= max_detections)

    # ── Count total ──
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # ── Paginate ──
    records = (
        query
        .order_by(desc(DetectionRecord.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # ── Map to response ──
    items = [
        DetectionResponse(
            id=r.id,
            created_at=r.created_at,
            num_detections=r.num_detections,
            result_image_url=f"/static/results/{Path(r.result_image_path).name}",
        )
        for r in records
    ]

    return HistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )