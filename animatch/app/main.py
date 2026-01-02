import base64
from fastapi import FastAPI, UploadFile, File, Body, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np 
import cv2
from animatch.app.services.explain import explain_match
from animatch.app.services.match import match_characters
from animatch.app.services.landmarks import extract_landmarks, draw_landmarks_on_image
from animatch.app.services.features import landmarks_to_features
from animatch.app.services.match import load_characters
app = FastAPI(title="Animatch")

# Allow local files and simple dev servers to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/inspect")#register a route that accepts post request 
async def inspect(file: UploadFile = File(...)):
    data = await file.read() #await allows it to pend
    
    arr = np.frombuffer(data, dtype=np.uint8) #converts bytes to list of num
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use jpg or png.")

    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    lighting_ok = brightness >= 60

    return {
        "width": w,
        "height": h,
        "brightness": round(brightness, 2),
        "lighting_ok": lighting_ok,
    }

@app.get("/characters")
def characters():
    chars = load_characters()
    return [{"id": c["id"], "name": c["name"], "series": c["series"], "tags": c.get("tags", [])} for c in chars]

@app.post("/match")
async def match(
    file: UploadFile = File(...),
    top_k: int = Query(3),
    debug: bool = Query(False),
    return_image: bool = Query(False, description="Return base64 PNG with plotted landmarks"),
):
    try:
        data = await file.read()

        landmarks, quality = extract_landmarks(data)
        if landmarks is None:
            raise HTTPException(status_code=400, detail="No face detected. Try better lighting and face the camera.")

        features = landmarks_to_features(landmarks)

        matches = match_characters(features, top_k=top_k)
        for m in matches:
            m["reasons"] = explain_match(features, m["vector"])

        resp = {
            "matches": matches,
            "quality": quality
        }

        if debug:
            resp["debug"] = {
                "features": features,
                "landmark_count": len(landmarks)
            }
        if return_image:
            overlay = draw_landmarks_on_image(data, landmarks)
            resp["debug_image_b64"] = base64.b64encode(overlay).decode("ascii")

        return resp
    except HTTPException:
        # already has status; just re-raise
        raise
    except Exception as exc:
        # Surface the error instead of generic 500 to simplify debugging in Swagger
        raise HTTPException(status_code=500, detail=f"Match failed: {exc}")


@app.post("/match/features")
def match_features(features = Body(...), top_k = 3): #features is the json the client sends, ... means body is required 
    matches = match_characters(features, top_k=top_k)

    for m in matches:
        m["reasons"] = explain_match(features, m["vector"])

    return {"matches": matches}
