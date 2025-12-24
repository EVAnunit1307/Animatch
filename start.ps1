# PowerShell start script for Animatch
# activate virtual env if present
if (Test-Path .venv/Scripts/Activate.ps1) {
  . .\.venv\Scripts\Activate.ps1
}

# Run the FastAPI app
python -m uvicorn animatch.app.main:app --reload --host 0.0.0.0 --port 8000
