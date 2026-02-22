from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class DetectionRecord(Base):
    """Bảng lưu lịch sử detect. Mỗi row = 1 lần upload + detect ảnh."""
    __tablename__ = "detection_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    num_detections = Column(Integer, nullable=False)
    image_path = Column(String(500), nullable=False)
    result_image_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)

    # Link tới Task (nullable vì records cũ không có)
    task_id = Column(String(36), nullable=True)

    def __repr__(self):
        return f"<DetectionRecord id={self.id} detections={self.num_detections}>"


class Task(Base):
    """Bảng theo dõi trạng thái xử lý async qua Kafka."""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True)  # UUID
    status = Column(String(20), default="processing")  # processing | completed | failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    original_filename = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)  # ảnh gốc upload

    # Kết quả (null khi chưa xử lý xong)
    num_detections = Column(Integer, nullable=True)
    result_image_path = Column(String(500), nullable=True)
    error_message = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<Task id={self.id} status={self.status}>"