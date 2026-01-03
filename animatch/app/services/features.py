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

LEFT_BROW = [70, 63, 105, 66, 107]
RIGHT_BROW = [300, 293, 334, 296, 336]
MOUTH_LEFT = 61
MOUTH_RIGHT = 291
NOSE_TIP = 1
NOSE_BRIDGE = 6


def dist2d(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx*dx + dy*dy)

def angle_at_point(a, b, c):
    """computes angle ABC with B as the vertex, uses dot prod"""
    ba = a[:2] - b[:2] #takes first 2, alt of [][]
    bc = a[:2] - c[:2]

    dot = float(ba[0]*bc[0] + ba[1] * bc[1])
    mag_ba = math.sqrt(float(ba[0]*ba[0] + ba[1]*ba[1]))
    mag_bc = math.sqrt(float(bc[0]*bc[0] + bc[1]*bc[1]))

    if mag_ba == 0 or mag_bc == 0:
        return 0.0
    
    angle_val = dot / (mag_ba * mag_bc)
    if angle_val > 1:  # clamp to avoid math domain errors
        angle_val = 1
    if angle_val < -1:
        angle_val = -1

    return math.acos(angle_val)  # radians



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
    chin = pts[ys.argmax()] # chin = lowest point (max y)

    # bottom region = last 15% of face height
    y_cut = ys.min() + 0.85 * face_height
    bottom_pts = pts[ys >= y_cut]

    # fallback
    if len(bottom_pts) < 5:
        bottom_pts = pts

    jaw_left = bottom_pts[bottom_pts[:, 0].argmin()]
    jaw_right = bottom_pts[bottom_pts[:, 0].argmax()]

    jaw_angle_rad = angle_at_point(jaw_left, chin, jaw_right)
    jaw_angle = jaw_angle_rad / math.pi  # normalize by dividing by pi


    chin_width = float(jaw_right[0] - jaw_left[0])
    chin_ratio = chin_width/face_width

    left_brow_y = float(np.mean([pts[i][1] for i in LEFT_BROW]))
    right_brow_y = float(np.mean([pts[i][1] for i in RIGHT_BROW]))

    left_lid_y = float(pts[LEFT_UPPER_LID][1])
    right_lid_y = float(pts[RIGHT_UPPER_LID][1])

    left_gap = (left_lid_y - left_brow_y) / face_height
    right_gap = (right_lid_y - right_brow_y) / face_height

    brow_height = (left_gap + right_gap) / 2

    mouth_left = pts[MOUTH_LEFT]
    mouth_right = pts[MOUTH_RIGHT]
    mouth_width_raw = dist2d(mouth_left, mouth_right)
    if face_width == 0:
        face_width = 1e-6
    mouth_width = mouth_width_raw / face_width

    nose_tip = pts[NOSE_TIP]
    nose_bridge = pts[NOSE_BRIDGE]
    nose_len_raw = dist2d(nose_tip, nose_bridge)
    nose_length = nose_len_raw / face_height


    return {
    "face_ratio": round(face_ratio, 4),
    "eye_spacing": round(eye_spacing, 4),
    "eye_openness": round(eye_openness, 4),
    "jaw_angle": round(jaw_angle, 4),
    "chin_ratio": round(chin_ratio, 4),
    "brow_height": round(brow_height, 4),
    "mouth_width": round(mouth_width, 4),
    "nose_length": round(nose_length, 4),
}
