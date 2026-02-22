from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routes import detection, history
from .kafka_producer import kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (settings.UPLOAD_DIR / "uploads").mkdir(parents=True, exist_ok=True)

    # Start Kafka producer
    await kafka_producer.start()

    yield

    # Shutdown
    await kafka_producer.stop()
    engine.dispose()

app = FastAPI(
    title="Object Counter API",
    description="API for object detection and counting",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files ──
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Routes ──
app.include_router(detection.router, prefix="/api", tags=["Detection"])
app.include_router(history.router, prefix="/api", tags=["History"])


@app.get("/health")
async def health():
    return {"status": "ok"}