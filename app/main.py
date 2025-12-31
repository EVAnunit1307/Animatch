"""
Lightweight adapter so you can run:
    uvicorn app.main:app --reload

It re-exports the real FastAPI instance from animatch.app.main.
"""
from animatch.app.main import app  # noqa: F401

