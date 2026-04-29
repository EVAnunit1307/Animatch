import base64
import json
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Body, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
from animatch.app.services.explain import explain_match
from animatch.app.services.match import match_characters, load_characters
from animatch.app.services.landmarks import extract_landmarks, draw_landmarks_on_image
from animatch.app.services.features import landmarks_to_features
app = FastAPI(title="Animatch")
from animatch.app.services import landmarks as landmarks_service

# preload model once at startup
landmarks_service._get_landmarker()

# Allow local files and simple dev servers to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="animatch/data"), name="static")
SERIES_POSTERS_PATH = Path("animatch/app/data/series_posters.json")

@app.get("/health")
def health():
    chars, _, mtime = load_characters()
    return {
        "status": "ok",
        "characters": len(chars),
        "dataset_mtime": mtime,
    }

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
    chars, _, _ = load_characters()
    return [{"id": c["id"], "name": c["name"], "series": c["series"], "tags": c.get("tags", []), "image_url": c.get("image_url")} for c in chars]


@app.get("/series")
def series():
    if SERIES_POSTERS_PATH.exists():
        return json.loads(SERIES_POSTERS_PATH.read_text(encoding="utf-8"))
    return []

def _run_match_pipeline(data: bytes, top_k: int, debug: bool, return_image: bool) -> dict:
    landmarks, quality = extract_landmarks(data)
    if landmarks is None:
        raise HTTPException(status_code=400, detail="No face detected. Try better lighting and face the camera.")

    features = landmarks_to_features(landmarks)

    matches = match_characters(features, top_k=top_k)
    for m in matches:
        m["reasons"] = explain_match(features, m["vector"])

    resp = {
        "matches": matches,
        "quality": {
            "brightness": quality.get("brightness"),
            "lighting_ok": quality.get("lighting_ok"),
            "angle_ok": quality.get("angle_ok"),
            "blur_score": quality.get("blur_score"),
            "sharpness_ok": quality.get("sharpness_ok"),
            "face_size_ok": quality.get("face_size_ok"),
            "confidence": quality.get("confidence"),
            "warnings": [],
        },
    }

    if debug:
        resp["debug"] = {
            "features": features,
            "landmark_count": len(landmarks),
        }
    if return_image:
        overlay = draw_landmarks_on_image(data, landmarks)
        resp["debug_image_b64"] = base64.b64encode(overlay).decode("ascii")

    warnings = []
    if not resp["quality"]["lighting_ok"]:
        warnings.append("Lighting is low")
    if not resp["quality"]["angle_ok"]:
        warnings.append("Face angle is off")
    if resp["quality"]["sharpness_ok"] is False:
        warnings.append("Image looks blurry")
    if resp["quality"]["face_size_ok"] is False:
        warnings.append("Face region is small")
    resp["quality"]["warnings"] = warnings

    return resp


async def _read_image_file(file: UploadFile) -> bytes:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (jpg/png).")

    data = await file.read()
    max_bytes = 5 * 1024 * 1024  # 5 MB
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail="File too large (max 5MB).")
    return data


@app.post("/match")
async def match(
    file: UploadFile = File(...),
    top_k: int = Query(4),
    debug: bool = Query(False),
    return_image: bool = Query(False, description="Return base64 PNG with plotted landmarks"),
):
    try:
        data = await _read_image_file(file)
        return _run_match_pipeline(data, top_k=top_k, debug=debug, return_image=return_image)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Match failed: {exc}")


@app.post("/match/features")
def match_features(features = Body(...), top_k = 4):
    matches = match_characters(features, top_k=top_k)

    for m in matches:
        m["reasons"] = explain_match(features, m["vector"])

    return {
        "matches": matches,
        "quality": None,
    }


@app.post("/describe")
async def describe(body: dict = Body(...)):
    name = body.get("name", "")
    series = body.get("series", "")
    reasons = body.get("reasons", [])

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        feature_phrases = [r.get("reason", "") for r in reasons[:3]]
        fallback = (
            f"Your facial geometry aligns with {name}'s distinctive features. "
            f"The analysis found {', '.join(feature_phrases).lower()} — "
            f"the quiet structural language that defines a {series} character."
        )
        return {"narrative": fallback, "source": "fallback"}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        feature_phrases = [r.get("reason", "") for r in reasons[:3]]
        prompt = (
            f"You matched someone to {name} from {series}. "
            f"The top matching facial features were: {', '.join(feature_phrases)}. "
            f"Write exactly 2 sentences — poetic, evocative, second-person ('Your...') — "
            f"about what this match reveals about the person's presence or essence. "
            f"Reference the character subtly. No em-dashes. No quotes around the output."
        )
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=120,
            messages=[{"role": "user", "content": prompt}],
        )
        narrative = message.content[0].text.strip()
        return {"narrative": narrative, "source": "claude"}
    except Exception as exc:
        feature_phrases = [r.get("reason", "") for r in reasons[:3]]
        fallback = (
            f"Your features carry the same {feature_phrases[0].lower() if feature_phrases else 'quiet intensity'} "
            f"as {name}. There is something in the geometry that speaks before words do."
        )
        return {"narrative": fallback, "source": "fallback"}
