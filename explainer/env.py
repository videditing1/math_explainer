"""Repo paths and API keys (.env at the repo root, never committed)."""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
VIDEOS = ROOT / "videos"
MEDIA = ROOT / "media"


def get_key(name: str, required: bool = True) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip()
    if required:
        raise SystemExit(f"{name} is not set. Add it to {env} (see .env.example).")
    return None
