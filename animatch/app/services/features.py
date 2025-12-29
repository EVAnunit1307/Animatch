import numpy as np
import math

LEFT_EYE_INNER = 133
RIGHT_EYE_INNER = 362

LEFT_EYE_OUTER = 33
RIGHT_EYE_OUTER = 263

LEFT_UPPER_LID = 159
LEFT_LOWER_LID = 145
RIGHT_UPPER_LID = 386
RIGHT_LOWER_LID = 374


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
    if face_height == 0: 
        face_height = 1e-6

    face_ratio = face_width / face_height
    left_inner = pts[LEFT_EYE_INNER]
    right_inner = pts[RIGHT_EYE_INNER]

    eye_spacing_raw = dist2d(left_inner, right_inner)
    eye_spacing = eye_spacing_raw / face_width #computes and normalizes eye distance
    """computes eye openess and converts geenral points to landmarks """
    left_outer = pts[LEFT_EYE_OUTER] 
    right_outer = pts[RIGHT_EYE_OUTER]

    left_upper = pts[LEFT_UPPER_LID]
    left_lower = pts[LEFT_LOWER_LID]
    right_upper = pts[RIGHT_UPPER_LID]
    right_lower = pts[RIGHT_LOWER_LID]

    left_eye_height = dist2d(left_upper, left_lower) #computes eye measurements 
    right_eye_height = dist2d(right_upper, right_lower)
    left_eye_width = dist2d(left_inner, left_outer)
    right_eye_width = dist2d(right_inner, right_outer)

    if left_eye_width == 0: #prevents dividing by 0
        left_eye_width = 1e-6
    if right_eye_width == 0:
        right_eye_width = 1e-6


    left_open = left_eye_height / left_eye_width #openness ratio
    right_open = right_eye_height / right_eye_width

    eye_openness = (left_open + right_open) / 2    #avrages



    return {
    "face_ratio": round(face_ratio, 4),
    "eye_spacing": round(eye_spacing, 4),
    "eye_openness": round(eye_openness, 4)
}
