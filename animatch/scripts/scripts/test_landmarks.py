import sys
import cv2
import mediapipe as mp

path = sys.argv[1]

img = cv2.imread(path)
if img is None:
    print("Could not read image file")
    sys.exit(1)

rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
)

results = face_mesh.process(rgb)

if not results.multi_face_landmarks:
    print("No face detected")
    sys.exit(0)

landmarks = results.multi_face_landmarks[0].landmark
print("Landmark count:", len(landmarks))
print("First landmark:", landmarks[0].x, landmarks[0].y, landmarks[0].z)
