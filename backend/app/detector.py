import cv2
import numpy as np
# import onnxruntime as ort
import tritonclient.grpc as grpcclient
from .config import settings
from .schemas import BBoxInfo


class PersonDetector:
    """
    YOLO26 person detector using ONNX Runtime.

    Output format: [1, 300, 6] — (x1, y1, x2, y2, confidence, class_id)
    Already NMS'd by the model, no need for manual NMS.
    """

    PERSON_CLASS_ID = 0
    INPUT_SIZE = 640

    def __init__(self, model_path: str = None, conf: float = None):
        # self.model_path = model_path or settings.MODEL_PATH
        # self.conf = conf or settings.CONFIDENCE_THRESHOLD
        # self.session: ort.InferenceSession | None = None
        # self._load_model()
        self.conf = conf or settings.CONFIDENCE_THRESHOLD
        self.model_name = settings.TRITON_MODEL_NAME
        self.client = grpcclient.InferenceServerClient(url=settings.TRITON_URL)

    # def _load_model(self):
    #     """Load ONNX model."""
    #     providers = ["CPUExecutionProvider"]
    #     self.session = ort.InferenceSession(self.model_path, providers=providers)

    #     input_info = self.session.get_inputs()[0]
    #     self.input_name = input_info.name

    def _preprocess(self, image: np.ndarray) -> tuple[np.ndarray, float, tuple[int, int]]:
        """
        Letterbox resize + normalize cho YOLO input.
        Trả về: (input_tensor, ratio, (pad_w, pad_h))
        """
        h, w = image.shape[:2]
        size = self.INPUT_SIZE

        # Tính ratio giữ tỷ lệ
        ratio = min(size / w, size / h)
        new_w, new_h = int(w * ratio), int(h * ratio)

        # Resize giữ tỷ lệ
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Letterbox pad về 640x640
        pad_w = (size - new_w) // 2
        pad_h = (size - new_h) // 2
        padded = np.full((size, size, 3), 114, dtype=np.uint8)
        padded[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized

        # BGR→RGB, HWC→CHW, 0-255→0-1
        blob = padded[:, :, ::-1].astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)
        blob = np.expand_dims(blob, 0)  # [1, 3, 640, 640]

        return blob, ratio, (pad_w, pad_h)

    def _postprocess(
        self, output: np.ndarray, ratio: float, pad: tuple[int, int]
    ) -> list[BBoxInfo]:
        """
        Xử lý YOLO26 output → danh sách BBoxInfo.

        YOLO26 output: [1, 300, 6]
        Mỗi detection: [x1, y1, x2, y2, confidence, class_id]
        Đã qua NMS trong model, không cần NMS thủ công.
        """
        detections = output[0]  # [300, 6]
        pad_w, pad_h = pad

        results = []
        for det in detections:
            x1, y1, x2, y2, conf, class_id = det

            # Chỉ lấy person (class 0) và trên ngưỡng confidence
            if int(class_id) != self.PERSON_CLASS_ID:
                continue
            if conf < self.conf:
                continue

            # Scale back to original image coordinates
            x1 = (x1 - pad_w) / ratio
            y1 = (y1 - pad_h) / ratio
            x2 = (x2 - pad_w) / ratio
            y2 = (y2 - pad_h) / ratio

            results.append(BBoxInfo(
                x1=int(x1),
                y1=int(y1),
                x2=int(x2),
                y2=int(y2),
                conf=round(float(conf), 4),
            ))

        return results

    def detect(self, image: np.ndarray) -> list[BBoxInfo]:
        """Detect người trong ảnh, trả về danh sách BBoxInfo."""
        blob, ratio, pad = self._preprocess(image)
        # outputs = self.session.run(None, {self.input_name: blob})
        input_tensor = grpcclient.InferInput("images", blob.shape, "FP32")
        input_tensor.set_data_from_numpy(blob)

        result = self.client.infer(
            model_name=self.model_name,
            inputs=[input_tensor]
        )

        output = result.as_numpy("output0")

        return self._postprocess(output, ratio, pad)

    def is_loaded(self) -> bool:
        return self.client.is_model_ready(self.model_name)
