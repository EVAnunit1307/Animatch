# Animatch ƒ?" Quick dev setup dY"

## Requirements
- Python 3.10+ (3.12 tested with MediaPipe Tasks)

---

## 1) Create and activate a virtual environment

PowerShell (Windows):

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1
```

cmd:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Bash (Git Bash / WSL):

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3) Start the app (FastAPI / Uvicorn)

```bash
python -m uvicorn animatch.app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://127.0.0.1:8000/health ƒ?" you should get `{"status":"ok"}`

---

## 4) Run the landmark script

The repo contains a top-level `scripts/` folder. To inspect an image and print face landmark counts:

```bash
# from project root
.venv\Scripts\python scripts\test_landmarks.py C:\path\to\selfie.jpg
```

By default the script uses the MediaPipe **Tasks** Face Landmarker (works on Python 3.12). On first run it downloads the model to `scripts/models/face_landmarker.task` unless you already supplied one. If you prefer to provide your own model file, run:

```bash
.venv\Scripts\python scripts\test_landmarks.py C:\path\to\selfie.jpg --model C:\path\to\face_landmarker.task --no-download
```

---

## Tips
- The script now uses the MediaPipe Tasks API (Face Landmarker). If the default download is blocked, supply your own `.task` file with `--model` and `--no-download`.
- If OpenCV `cv2.imread` returns `None`, check the path and file format; this script now exits with a helpful message when that happens.

Happy testing! ƒo.
