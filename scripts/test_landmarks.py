#!/usr/bin/env python3
"""Count face landmarks using the MediaPipe Tasks FaceLandmarker (works on Python 3.12).

Usage:
  python scripts/test_landmarks.py path/to/image.jpg

Options:
  --model PATH        Use a custom .task model file (defaults to scripts/models/face_landmarker.task)
  --no-download       Fail if the model file is missing instead of downloading the default one
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import mediapipe as mp
import requests
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

DEFAULT_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float32/1/face_landmarker.task"
)
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "face_landmarker.task"


def ensure_tasks_available() -> None:
    """Abort early with a helpful message if this mediapipe build lacks Tasks."""
    if not hasattr(mp, "tasks"):
        print(
            "This mediapipe build does not expose the Tasks API required for Python 3.12.\n"
            "Install a Tasks-enabled version (e.g. mediapipe>=0.10.0).",
            file=sys.stderr,
        )
        sys.exit(1)


def download_model(model_path: Path, url: str = DEFAULT_MODEL_URL) -> Path:
    """Download the Face Landmarker .task file to the requested location."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading MediaPipe face_landmarker model to {model_path} ...")
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Download failed: {exc}") from exc

    with open(model_path, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                fh.write(chunk)

    return model_path


def resolve_model_path(path_arg: Optional[str], allow_download: bool) -> Path:
    """Return a usable model path, downloading the default model if allowed."""
    model_path = Path(path_arg).expanduser() if path_arg else DEFAULT_MODEL_PATH
    if model_path.exists():
        return model_path

    if not allow_download:
        raise SystemExit(
            f"Model not found: {model_path}\n"
            "Provide --model PATH or rerun without --no-download to fetch the default model."
        )

    try:
        return download_model(model_path)
    except Exception as exc:
        raise SystemExit(
            f"Failed to obtain model at {model_path}\n"
            f"Attempted to download from: {DEFAULT_MODEL_URL}\n"
            f"Error: {exc}"
        )


def load_image(path: Path) -> mp.Image:
    """Load an image from disk into a MediaPipe Image."""
    try:
        return mp.Image.create_from_file(str(path))
    except Exception as exc:
        raise SystemExit(f"Could not read image file: {path}\nError: {exc}")


def main() -> None:
    ensure_tasks_available()

    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to image file (jpg/png/...) to inspect")
    parser.add_argument(
        "--model",
        help="Path to a MediaPipe Face Landmarker .task file (default: scripts/models/face_landmarker.task)",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Fail if the default model is missing instead of downloading it automatically",
    )
    args = parser.parse_args()

    image_path = Path(args.image).expanduser()
    if not image_path.exists():
        raise SystemExit(
            f"File not found: {image_path}\n"
            "Provide a valid image path. Example:\n"
            r"  .venv\Scripts\python scripts\test_landmarks.py C:\Users\<you>\Pictures\selfie.jpg"
        )

    model_path = resolve_model_path(args.model, allow_download=not args.no_download)
    mp_image = load_image(image_path)

    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )
    landmarker = vision.FaceLandmarker.create_from_options(options)
    result = landmarker.detect(mp_image)

    if not result.face_landmarks:
        print("No face detected")
        return

    landmarks = result.face_landmarks[0]
    print("Landmark count:", len(landmarks))
    first = landmarks[0]
    print("First landmark:", first.x, first.y, first.z)


if __name__ == "__main__":
    main()
