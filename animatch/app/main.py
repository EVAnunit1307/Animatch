from fastapi import FastAPI, UploadFile, File, HTTPException
import numpy as np 
import cv2

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
