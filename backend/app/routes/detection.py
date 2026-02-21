import cv2
import numpy as np
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..detector import PersonDetector
from ..visualizer import draw_boxes, save_result
from ..models import DetectionRecord
from ..schemas import DetectionResponse, BBoxInfo, DetailedDetectionResponse

router = APIRouter()
detector = PersonDetector()


@router.post("/detect", response_model=DetailedDetectionResponse)
async def detect_person(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload ảnh → Detect người → Trả kết quả."""

    # 1. Check file type
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only accepted JPEG, PNG, WebP")

    # 2. Read image
    image_bytes = await file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(400, "Cannot read image file")

    # 3. Detect
    boxes = detector.detect(image)

    # 4. Visualize
    annotated = draw_boxes(image, boxes)

    # 5. Save
    result_path = save_result(annotated, prefix="result")
    original_path = save_result(image, prefix="original")

    # 6. Store DB
    record = DetectionRecord(
        num_detections=len(boxes),
        image_path=original_path,
        result_image_path=result_path,
        original_filename=file.filename or "unknown",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 7. Response
    return DetailedDetectionResponse(
        id=record.id,
        created_at=record.created_at,
        num_detections=len(boxes),
        result_image_url=f"/static/results/{Path(result_path).name}",
        boxes=[
            BBoxInfo(
                x1=b.x1, y1=b.y1, x2=b.x2, y2=b.y2,
                conf=b.conf,
            )
            for b in boxes
        ],
    )