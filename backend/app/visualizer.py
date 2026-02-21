import cv2
import numpy as np
import uuid
from pathlib import Path
from datetime import datetime
from .schemas import BBoxInfo
from .config import settings


# ── Style constants ──
BOX_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)
BOX_THICKNESS = 2
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.6


def draw_boxes(image: np.ndarray, boxes: list[BBoxInfo]) -> np.ndarray:
    """Vẽ bounding boxes lên ảnh. Trả về ảnh mới (không modify gốc)."""
    annotated = image.copy()

    for i, box in enumerate(boxes):
        # Vẽ rectangle
        cv2.rectangle(
            annotated,
            (box.x1, box.y1),
            (box.x2, box.y2),
            BOX_COLOR,
            BOX_THICKNESS,
        )

        # Label: "Person 0.92"
        label = f"Person {box.conf:.2f}"

        # Background cho text
        (text_w, text_h), baseline = cv2.getTextSize(label, FONT, FONT_SCALE, 1)
        cv2.rectangle(
            annotated,
            (box.x1, box.y1 - text_h - baseline - 4),
            (box.x1 + text_w, box.y1),
            BOX_COLOR,
            cv2.FILLED,
        )

        cv2.putText(
            annotated, label,
            (box.x1, box.y1 - baseline - 2),
            FONT, FONT_SCALE, TEXT_COLOR, 1,
        )

    return annotated


def save_result(image: np.ndarray, prefix: str = "result") -> str:
    """Lưu ảnh kết quả vào static/results/. Trả về relative path."""
    output_dir = settings.UPLOAD_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{prefix}_{timestamp}_{unique_id}.jpg"

    filepath = output_dir / filename
    cv2.imwrite(str(filepath), image)

    return str(filepath)
