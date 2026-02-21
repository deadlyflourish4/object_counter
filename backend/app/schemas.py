from pydantic import BaseModel, Field
from datetime import datetime, date


class DetectionResponse(BaseModel):
    """Response cho POST /api/detect."""
    id: int
    created_at: datetime
    num_detections: int
    result_image_url: str

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    """Response phân trang cho danh sách lịch sử."""
    items: list[DetectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class HistoryQuery(BaseModel):
    """Filter/search params cho trang History."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    min_detections: int | None = None
    max_detections: int | None = None


class BBoxInfo(BaseModel):
    """Thông tin 1 bounding box."""
    x1: int
    y1: int
    x2: int
    y2: int
    conf: float
    label: str = "person"


class DetailedDetectionResponse(DetectionResponse):
    """Response mở rộng kèm danh sách bounding boxes."""
    boxes: list[BBoxInfo] = []