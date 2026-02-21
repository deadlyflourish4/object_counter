from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Cấu hình ứng dụng, đọc từ .env hoặc environment variables."""

    # ── Database ──
    DATABASE_URL: str = "postgresql://counter:counter_pass@localhost:5432/object_counter"

    # ── YOLO Model ──
    MODEL_PATH: str = "models/yolo26m.onnx"
    CONFIDENCE_THRESHOLD: float = 0.5

    # ── File Storage ──
    UPLOAD_DIR: Path = Path("static/results")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # ── CORS ──
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Singleton instance
settings = Settings()
