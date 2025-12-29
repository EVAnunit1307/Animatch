
import cv2
import numpy as np
import mediapipe as mp


def decode_image(image_bytes):
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Unsupported format or corrupted bytes.")
    return img

def get_brightness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))

face_mesh = None

def get_face_mesh():
    global face_mesh
    if face_mesh is None:
        face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
        )
    return face_mesh

def extract_landmarks(image_bytes):
    img = decode_image(image_bytes)
    info = {"face_detected": False, "lighting_ok": False, "brightness": None}

    if img is None:
        return None, info

    brightness = get_brightness(img)
    info["brightness"] = round(brightness, 2)
    info["lighting_ok"] = brightness >= 60

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = get_face_mesh().process(rgb)

    if not result.multi_face_landmarks:
        return None, info

    lms = result.multi_face_landmarks[0].landmark
    landmarks = [(p.x, p.y, p.z) for p in lms]

    info["face_detected"] = True
    return landmarks, info



