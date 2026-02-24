# Animatch

Live demo: [https://vercel.com/evans-projects-37167e00/animatch](https://animatch-psi.vercel.app/)

Local-first anime face matching. Upload a photo, extract MediaPipe FaceMesh landmarks, compare normalized face ratios against an anime character dataset, and return the closest matches with visuals.

# What it does
- Extracts 500+ face landmarks with MediaPipe Tasks Face Landmarker.
- Computes normalized facial ratios (eyes, jaw, chin, brow, mouth, nose).
- Ranks against an anime character vector dataset.
- Returns top matches plus optional landmark overlays.

# Tech stack
- FastAPI + Uvicorn
- MediaPipe (Tasks Face Landmarker)
- OpenCV + NumPy
- React 

# Requirements
- Python 3.12

# Quick start
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

# Endpoints
- `GET /health` -> status
- `POST /match` -> upload image + match results
- `GET /characters` -> dataset used by the UI reel
- `GET /series` -> featured series list

# Local landmark test
Run a quick landmark check without the API:
```bash
python scripts/test_landmarks.py C:\path\to\selfie.jpg
```

This script downloads the Face Landmarker model to `scripts/models/face_landmarker.task` on first run.
If you already have the model, pass `--model` and `--no-download`.

# Dataset build (optional)
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

# Project layout
- `animatch/app` - API backend
- `animatch/app/data` - JSON datasets used by the API/UI
- `animatch/data` - raw downloads, batches, overlays
- `frontend.html` - UI
- `scripts/` - dataset and tooling scripts

# Notes
- The API downloads the MediaPipe model to `animatch/app/models/face_landmarker.task` on first run.
- If downloads are blocked, place the model at that path before starting the API.

# Deployment (web app)
This works as a simple web app as long as the dataset files are shipped with the deploy:
- `animatch/app/data/anime_vectors.json`
- `animatch/app/data/series_posters.json`

If those are present, anyone can open the site, take a photo, and get matches without rebuilding the dataset.

# Phone + camera access
- Camera capture requires HTTPS. Local file paths will not work.
- When deployed, make sure your frontend is served over HTTPS and points to the live API URL.

> Random edit: some random shit added here just to create commits and chaos.

# Deploy to Railway (API)
1) Create a new Railway project from this repo.
2) Railway will use `railway.toml` / `Procfile` to start the API.
3) Deploy and copy the public URL (e.g. `https://your-service.up.railway.app`).

# Deploy to Vercel (Frontend)
1) Create a new Vercel project from this repo.
2) Framework preset: Other.
3) Build command: leave empty.
4) Output directory: leave empty (Vercel serves `frontend.html`).
5) After deploy, open the Vercel URL with `?api=` pointing to Railway:
   - Example: `https://your-vercel-app.vercel.app/?api=https://your-service.up.railway.app`
6) The `?api=` value is stored in `localStorage` as `ANIMATCH_API_BASE` for next visits.
