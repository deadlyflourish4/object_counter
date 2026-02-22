"""
Batch inference — gửi hàng loạt ảnh tới API.

Cách dùng:
  python batch_detect.py ./images/              # sync mode
  python batch_detect.py ./images/ --async      # async mode (Kafka)
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE = os.getenv("API_URL", "http://localhost:8000")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def detect_sync(image_path: Path) -> dict:
    """POST /api/detect — chờ kết quả."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/api/detect",
            files={"file": (image_path.name, f, "image/jpeg")},
        )
    resp.raise_for_status()
    return resp.json()


def detect_async(image_path: Path) -> dict:
    """POST /api/detect/async — trả task_id."""
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{API_BASE}/api/detect/async",
            files={"file": (image_path.name, f, "image/jpeg")},
        )
    resp.raise_for_status()
    return resp.json()


def poll_task(task_id: str, timeout: int = 60) -> dict:
    """Polling GET /api/tasks/{task_id} cho tới khi hoàn thành."""
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{API_BASE}/api/tasks/{task_id}")
        data = resp.json()
        if data["status"] in ("completed", "failed"):
            return data
        time.sleep(0.5)
    return {"status": "timeout", "task_id": task_id}


def main():
    parser = argparse.ArgumentParser(description="Batch detection")
    parser.add_argument("folder", help="Thư mục chứa ảnh")
    parser.add_argument("--async", dest="use_async", action="store_true",
                        help="Dùng async mode (Kafka)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Số thread song song (default: 4)")
    args = parser.parse_args()

    folder = Path(args.folder)
    images = [f for f in folder.iterdir()
              if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]

    if not images:
        print(f"Không tìm thấy ảnh trong {folder}")
        sys.exit(1)

    print(f"📂 Tìm thấy {len(images)} ảnh trong {folder}")
    print(f"🔧 Mode: {'Async (Kafka)' if args.use_async else 'Sync'}")
    print(f"🧵 Workers: {args.workers}")
    print("-" * 50)

    start_time = time.time()
    results = []

    if args.use_async:
        # Gửi tất cả async, rồi poll kết quả
        task_ids = []
        for img in images:
            data = detect_async(img)
            task_ids.append((img.name, data["task_id"]))
            print(f"  📤 {img.name} → task_id: {data['task_id']}")

        print("\n⏳ Đang chờ kết quả...")
        for name, task_id in task_ids:
            result = poll_task(task_id)
            detections = result.get("num_detections", "?")
            status = result["status"]
            print(f"  {'✅' if status == 'completed' else '❌'} {name}: {detections} người ({status})")
            results.append(result)
    else:
        # Gửi song song sync
        def process(img):
            result = detect_sync(img)
            return img.name, result

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(process, img): img for img in images}
            for future in as_completed(futures):
                name, result = future.result()
                detections = result.get("num_detections", "?")
                print(f"  ✅ {name}: {detections} người")
                results.append(result)

    elapsed = time.time() - start_time
    print("-" * 50)
    print(f"🏁 Xong! {len(images)} ảnh trong {elapsed:.1f}s")
    print(f"   Trung bình: {elapsed/len(images):.2f}s/ảnh")
    print(f"   Throughput: {len(images)/elapsed:.1f} ảnh/s")


if __name__ == "__main__":
    main()
