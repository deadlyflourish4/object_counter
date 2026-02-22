import uuid
import cv2
import numpy as np
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..detector import PersonDetector
from ..visualizer import draw_boxes, save_result
from ..kafka_producer import kafka_producer
from ..models import DetectionRecord, Task
from ..schemas import (
    DetectionResponse,
    BBoxInfo,
    DetailedDetectionResponse,
    TaskSubmitResponse,
    TaskStatusResponse,
)
from ..config import settings

router = APIRouter()
detector = PersonDetector()


@router.post("/detect", response_model=DetailedDetectionResponse)
async def detect_person_sync(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Synchronous detection — chờ kết quả rồi trả về.
    Giữ lại endpoint cũ cho backward compatibility.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only accepted JPEG, PNG, WebP")

    image_bytes = await file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(400, "Cannot read image file")

    boxes = detector.detect(image)
    annotated = draw_boxes(image, boxes)

    result_path = save_result(annotated, prefix="result")
    original_path = save_result(image, prefix="original")

    record = DetectionRecord(
        num_detections=len(boxes),
        image_path=original_path,
        result_image_path=result_path,
        original_filename=file.filename or "unknown",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return DetailedDetectionResponse(
        id=record.id,
        created_at=record.created_at,
        num_detections=len(boxes),
        result_image_url=f"/static/results/{Path(result_path).name}",
        boxes=[
            BBoxInfo(x1=b.x1, y1=b.y1, x2=b.x2, y2=b.y2, conf=b.conf)
            for b in boxes
        ],
    )


@router.post("/detect/async", response_model=TaskSubmitResponse)
async def detect_person_async(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Async detection qua Kafka — trả task_id ngay, worker xử lý sau.
    Client dùng GET /api/tasks/{task_id} để check kết quả.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Only accepted JPEG, PNG, WebP")

    # 1. Tạo task_id
    task_id = str(uuid.uuid4())

    # 2. Lưu ảnh gốc ra disk
    image_bytes = await file.read()
    upload_dir = settings.UPLOAD_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    image_path = upload_dir / f"{task_id}.jpg"
    image_path.write_bytes(image_bytes)

    # 3. Tạo Task record trong DB (status=processing)
    task = Task(
        id=task_id,
        status="processing",
        original_filename=file.filename or "unknown",
        image_path=str(image_path),
    )
    db.add(task)
    db.commit()

    # 4. Gửi message vào Kafka
    await kafka_producer.send_detection_request(
        task_id=task_id,
        image_path=str(image_path),
        original_filename=file.filename or "unknown",
    )

    # 5. Trả task_id ngay (~100ms)
    return TaskSubmitResponse(task_id=task_id, status="processing")


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
):
    """Query trạng thái task async."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, f"Task {task_id} not found")

    result_image_url = None
    if task.result_image_path:
        result_image_url = f"/static/results/{Path(task.result_image_path).name}"

    return TaskStatusResponse(
        task_id=task.id,
        status=task.status,
        created_at=task.created_at,
        completed_at=task.completed_at,
        original_filename=task.original_filename,
        num_detections=task.num_detections,
        result_image_url=result_image_url,
        error_message=task.error_message,
    )