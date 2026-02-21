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

    def __repr__(self):
        return f"<DetectionRecord id={self.id} detections={self.num_detections}>"