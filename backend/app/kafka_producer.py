from aiokafka import AIOKafkaProducer
import json
from datetime import datetime

from .config import settings

TOPIC = settings.KAFKA_TOPIC


class KafkaProducer:
    """Async Kafka producer cho detection pipeline."""

    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_detection_request(
        self, task_id: str, image_path: str, original_filename: str
    ):
        message = {
            "task_id": task_id,
            "image_path": image_path,
            "original_filename": original_filename,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.producer.send_and_wait(TOPIC, message)


# Singleton instance — start/stop trong main.py lifespan
kafka_producer = KafkaProducer()