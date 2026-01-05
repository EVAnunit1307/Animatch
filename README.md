# Animatch

Local-first anime face matching. Upload a photo, extract MediaPipe FaceMesh landmarks, compare normalized face ratios against an anime character dataset, and return the closest matches with visuals.

## What it does
- Extracts 468 face landmarks with MediaPipe Tasks Face Landmarker.
- Computes normalized facial ratios (eyes, jaw, chin, brow, mouth, nose).
- Ranks against an anime character vector dataset.
- Returns top matches plus optional landmark overlays.

## Tech stack
- FastAPI + Uvicorn
- MediaPipe (Tasks Face Landmarker)
- OpenCV + NumPy

## Requirements
- Python 3.12

## Quick start
1) Create and activate a virtual environment

PowerShell:
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Start the API
```bash
python -m uvicorn animatch.app.main:app --reload --host 127.0.0.1 --port 8000
```

4) Open the docs
```
http://127.0.0.1:8000/docs
```

5) Run the UI (recommended)
```bash
python -m http.server 5500
```
Open:
```
http://127.0.0.1:5500/frontend.html
```

Note: the camera capture only works on http(s), not a local file path.

## Endpoints
- `GET /health` -> status
- `POST /match` -> upload image + match results
- `GET /characters` -> dataset used by the UI reel
- `GET /series` -> featured series list

## Local landmark test
Run a quick landmark check without the API:
```bash
python scripts/test_landmarks.py C:\path\to\selfie.jpg
```

This script downloads the Face Landmarker model to `scripts/models/face_landmarker.task` on first run.
If you already have the model, pass `--model` and `--no-download`.

## Dataset build (optional)
The repo includes scripts to rebuild the dataset:

```bash
python scripts/build_series_posters.py
python scripts/fetch_all_series.py
python scripts/auto_select_characters.py
python scripts/split_handpicked_batches.py --size 60
python scripts/run_batches_merge.py --batch-dir animatch/data/batches_auto
```

Outputs:
- `animatch/app/data/series_posters.json`
- `animatch/app/data/anime_vectors.json`

## Project layout
- `animatch/app` - API backend
- `animatch/app/data` - JSON datasets used by the API/UI
- `animatch/data` - raw downloads, batches, overlays
- `frontend.html` - UI
- `scripts/` - dataset and tooling scripts

## Notes
- The API downloads the MediaPipe model to `animatch/app/models/face_landmarker.task` on first run.
- If downloads are blocked, place the model at that path before starting the API.

## Deployment (web app)
This works as a simple web app as long as the dataset files are shipped with the deploy:
- `animatch/app/data/anime_vectors.json`
- `animatch/app/data/series_posters.json`

If those are present, anyone can open the site, take a photo, and get matches without rebuilding the dataset.

### Phone + camera access
- Camera capture requires HTTPS. Local file paths won’t work.
- When deployed, make sure your frontend is served over HTTPS and points to the live API URL.

### Vercel
Vercel is great for the static frontend, but the FastAPI backend and MediaPipe model download are better hosted on a Python server (Render, Railway, Fly.io, or a VPS). You can still deploy the UI on Vercel and point it to your API base URL.

If you want a single-host setup on Vercel, we can package the API as a serverless function, but MediaPipe model size and cold starts may be limiting. For production, a dedicated Python host is smoother.
