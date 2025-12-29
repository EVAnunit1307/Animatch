import numpy as np
import math

LEFT_EYE_INNER = 133
RIGHT_EYE_INNER = 362

def dist2d(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx*dx + dy*dy)


def landmarks_to_features(landmarks):
    pts = np.array(landmarks, dtype=np.float32)  # shape: (N, 3)

    xs = pts[:, 0]
    ys = pts[:, 1]

    face_width = float(xs.max() - xs.min())
    face_height = float(ys.max() - ys.min())

    
    if face_width == 0: #prevents dividing by 0
        face_width = 1e-6

    if face_height == 0: #prevents dividing by 0
        face_height = 1e-6

    face_ratio = face_width / face_height
    left_inner = pts[LEFT_EYE_INNER]
    right_inner = pts[RIGHT_EYE_INNER]

    eye_spacing_raw = dist2d(left_inner, right_inner)
    eye_spacing = eye_spacing_raw / face_width #computes and normalizes eye distance

    return {
        "face_ratio": round(face_ratio, 4),
        "eye_spacing": round(eye_spacing, 4)
    }
