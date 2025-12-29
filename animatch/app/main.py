from fastapi import FastAPI, UploadFile, File, Body, HTTPException
import numpy as np 
import cv2
from animatch.app.services.explain import explain_match
from animatch.app.services.match import match_characters
from animatch.app.services.landmarks import extract_landmarks
app = FastAPI(title="Animatch")

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

@app.post("/match")
async def match(file: UploadFile = File(...)):
    data = await file.read()
    landmarks, quality = extract_landmarks(data)

    if landmarks is None:
        raise HTTPException(status_code=400, detail="No face detected. Try better lighting and face the camera.")

    return {"landmark_count": len(landmarks), "quality": quality}

@app.post("/match/features")
def match_features(features = Body(...), top_k = 3): #features is the json the client sends, ... means body is required 
    matches = match_characters(features, top_k=top_k)

    for m in matches:
        m["reasons"] = explain_match(features, m["vector"])

    return {"matches": matches}

