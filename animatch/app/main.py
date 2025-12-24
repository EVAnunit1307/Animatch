from fastapi import FastAPI, UploadFile, File
import numpy as np 
import cv2

app = FastAPI(title="Animatch")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/inspect")#register a route that accepts post request 
async def inspect(file: UploadFile = File(...)):
    data = await file.read() #await allows it to pend
    return {"bytes": len(data)}

   
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Use jpg or png.")

    h, w = img.shape[:2]
    return {"width": w, "height": h}