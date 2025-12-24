#!/usr/bin/env bash
set -e

# activate venv if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Run the FastAPI app (module path: animatch.app.main:app)
uvicorn animatch.app.main:app --reload --host 0.0.0.0 --port 8000
