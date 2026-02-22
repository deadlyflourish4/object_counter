"""
Kafka Consumer Worker — chạy riêng biệt khỏi FastAPI.

Đọc message từ topic "detection-requests", chạy inference qua Triton,
lưu kết quả vào DB.

Chạy: python -m worker
"""

import json
import asyncio
import cv2
import numpy as np
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.detector import PersonDetector
from app.visualizer import draw_boxes, save_result
from app.models import Task, DetectionRecord


# Khởi tạo detector (Triton client)
detector = PersonDetector()


async def process_message(data: dict):
    """Xử lý 1 detection request từ Kafka."""
    task_id = data["task_id"]
    image_path = data["image_path"]
    original_filename = data.get("original_filename", "unknown")

    db: Session = SessionLocal()
    try:
        # 1. Đọc ảnh từ disk
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        # 2. Detect qua Triton
        boxes = detector.detect(image)

        # 3. Visualize
        annotated = draw_boxes(image, boxes)

        # 4. Lưu ảnh kết quả
        result_path = save_result(annotated, prefix="result")
        original_path = save_result(image, prefix="original")

        # 5. Lưu DetectionRecord
        record = DetectionRecord(
            num_detections=len(boxes),
            image_path=original_path,
            result_image_path=result_path,
            original_filename=original_filename,
            task_id=task_id,
        )
        db.add(record)

        # 6. Update Task status → completed
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.num_detections = len(boxes)
            task.result_image_path = result_path

        db.commit()
        print(f"✅ Task {task_id}: {len(boxes)} detections")

    except Exception as e:
        # Update Task status → failed
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "failed"
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)[:1000]
            db.commit()
        print(f"❌ Task {task_id} failed: {e}")

    finally:
        db.close()


async def main():
    """Main consumer loop."""
    print(f"🚀 Worker starting...")
    print(f"   Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"   Topic: {settings.KAFKA_TOPIC}")
    print(f"   Triton: {settings.TRITON_URL}")

    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="detection-workers",
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    await consumer.start()
    print("✅ Worker connected to Kafka, waiting for messages...")

    try:
        async for message in consumer:
            data = message.value
            print(f"📩 Received task: {data['task_id']}")
            await process_message(data)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
