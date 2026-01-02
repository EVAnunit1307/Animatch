import math
from pathlib import Path
from typing import Optional, Tuple, List

import cv2
import numpy as np
import requests
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "face_landmarker.task"

_landmarker: Optional[vision.FaceLandmarker] = None


def _ensure_model(path: Path = MODEL_PATH) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(MODEL_URL, stream=True, timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                fh.write(chunk)
    return path


def _get_landmarker() -> vision.FaceLandmarker:
    global _landmarker
    if _landmarker is None:
        model_path = _ensure_model()
        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
    return _landmarker


def decode_image(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Unsupported format or corrupted bytes.")
    return img


def get_brightness(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def get_blur_score(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def face_size_ok(landmarks: List[Tuple[float, float, float]], width: int, height: int, min_ratio: float = 0.15) -> bool:
    xs = [p[0] * width for p in landmarks]
    ys = [p[1] * height for p in landmarks]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (w / width) >= min_ratio and (h / height) >= min_ratio


def extract_landmarks(image_bytes: bytes) -> Tuple[Optional[List[Tuple[float, float, float]]], dict]:
    """
    Returns (landmarks, info). landmarks is a list of (x, y, z) or None if no face.
    info contains brightness, lighting_ok, face_detected flags.
    """
    img = decode_image(image_bytes)
    info = {
        "face_detected": False,
        "lighting_ok": False,
        "brightness": None,
        "blur_score": None,
        "sharpness_ok": False,
        "face_size_ok": False,
    }

    brightness = get_brightness(img)
    info["brightness"] = round(brightness, 2)
    info["lighting_ok"] = brightness >= 60
    blur_score = get_blur_score(img)
    info["blur_score"] = round(blur_score, 2)
    info["sharpness_ok"] = blur_score >= 30.0

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    result = _get_landmarker().detect(mp_image)

    if not result.face_landmarks:
        return None, info

    lms = result.face_landmarks[0]
    landmarks = [(p.x, p.y, p.z) for p in lms]

    angle_ok = angle_ok_from_landmarks(landmarks)
    info["angle_ok"] = angle_ok
    info["face_size_ok"] = face_size_ok(landmarks, img.shape[1], img.shape[0])
    info["face_detected"] = True

    # simple confidence score
    conf = 0.0
    if info["face_detected"]:
        conf += 0.5
    if info["lighting_ok"]:
        conf += 0.25
    if info["angle_ok"]:
        conf += 0.25
    if not info["sharpness_ok"]:
        conf -= 0.1
    if not info["face_size_ok"]:
        conf -= 0.1
    info["confidence"] = round(conf, 2)

    return landmarks, info


LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263


def angle_ok_from_landmarks(landmarks: List[Tuple[float, float, float]]) -> bool:
    """
    Heuristic frontal/roll check using eye corners.
    Returns True if the roll angle is within a small threshold.
    """
    try:
        left = landmarks[LEFT_EYE_OUTER]
        right = landmarks[RIGHT_EYE_OUTER]
    except Exception:
        return False

    dx = right[0] - left[0]
    dy = right[1] - left[1]
    if dx == 0 and dy == 0:
        return False

    roll = abs(math.atan2(dy, dx))  # radians
    return roll < 0.2  # ~11 degrees


def draw_landmarks_on_image(
    image_bytes: bytes, landmarks: List[Tuple[float, float, float]], radius: int = None
) -> bytes:
    """
    Draw landmarks on the input image and return PNG bytes.
    Radius auto scales to image size if not provided.
    """
    img = decode_image(image_bytes)
    h, w = img.shape[:2]

    # auto-scale radius to image size; keep a minimum so small images still visible
    if radius is None:
        radius = max(1, int(min(h, w) * 0.003) - 1)

    for x, y, _ in landmarks:
        px = int(x * w)
        py = int(y * h)
        cv2.circle(img, (px, py), radius, (0, 255, 0), thickness=-1)

    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise ValueError("Could not encode debug image.")
    return buf.tobytes()
