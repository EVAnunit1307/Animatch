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

def angle_ok_from_landmarks(landmarks):
    # landmarks are list of (x,y,z) normalized
    nose = landmarks[1]
    left_eye = landmarks[133]
    right_eye = landmarks[362]

    left_dx = abs(left_eye[0] - nose[0])
    right_dx = abs(right_eye[0] - nose[0])

    if right_dx == 0:
        return False

    ratio = left_dx / right_dx
    # if ratio is far from 1, face is likely turned
    return 0.65 <= ratio <= 1.55


def extract_landmarks(image_bytes: bytes) -> Tuple[Optional[List[Tuple[float, float, float]]], dict]:
    """
    Returns (landmarks, info). landmarks is a list of (x, y, z) or None if no face.
    info contains brightness, lighting_ok, face_detected flags.
    """
    img = decode_image(image_bytes)
    info = {"face_detected": False, "lighting_ok": False, "brightness": None}

    brightness = get_brightness(img)
    info["brightness"] = round(brightness, 2)
    info["lighting_ok"] = brightness >= 60

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    result = _get_landmarker().detect(mp_image)

    if not result.face_landmarks:
        return None, info

    lms = result.face_landmarks[0]
    landmarks = [(p.x, p.y, p.z) for p in lms]

    info["face_detected"] = True
    return landmarks, info


