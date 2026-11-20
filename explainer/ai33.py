"""AI33 / OpenSpeaker text-to-speech (ElevenLabs voices) with per-word timings.

API (from the docs built into the ai33.pro web app; there are no public docs):
  POST /v3/text-to-speech   multipart: text, voice_id (provider-prefixed, e.g.
                            "elevenlabs_<id>"), speed 0.5-1.5, with_transcript
                            -> {success, task_id}
  GET  /v1/task/{id}        poll until status "done" | "error";
                            metadata.audio_url / json_url (word timings) / srt_url
  GET  /v1/credits          balance;   GET /v2/voices  ElevenLabs voice list
Auth: header `xi-api-key: <AI33_API_KEY>`.
"""
from __future__ import annotations

import json
import pathlib
import time
import urllib.request
import uuid

from .env import get_key

BASE = "https://api.ai33.pro"

VOICES = {  # handy defaults; full list: `explainer voices`
    "george": "elevenlabs_JBFqnCBsd6RMkjVDRZzb",   # warm British storyteller (default)
    "river": "elevenlabs_SAz9YHcvj6GT2YYXdXww",    # relaxed, neutral, informative
    "bella": "elevenlabs_hpp4J3VqNfWAUOO0d1Us",    # bright, warm, educational
    "roger": "elevenlabs_CwhRBWXzGAHq8TQ4Fs17",    # laid-back, resonant
    "sarah": "elevenlabs_EXAVITQu4vr4xnSDxMaL",    # mature, reassuring
}


def _request(method, path, data=None, headers=None):
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"xi-api-key": get_key("AI33_API_KEY"), **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def download(url: str, dest: pathlib.Path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # CDN blocks urllib's UA
    with urllib.request.urlopen(req, timeout=180) as r:
        pathlib.Path(dest).write_bytes(r.read())


def credits() -> int:
    return _request("GET", "/v1/credits").get("credits", 0)


def voices() -> list[dict]:
    return _request("GET", "/v2/voices")["voices"]


def synthesize(text: str, folder: pathlib.Path, voice: str = "george", speed: float = 1.0,
               log=print) -> pathlib.Path:
    """Generate folder/voice.mp3 + voice.timing.json + voice.srt. Returns the mp3 path."""
    voice_id = VOICES.get(voice, voice)
    boundary = uuid.uuid4().hex
    fields = {"text": text, "voice_id": voice_id, "speed": str(speed), "with_transcript": "true"}
    body = b"".join(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
                    for k, v in fields.items()) + f"--{boundary}--\r\n".encode()
    created = _request("POST", "/v3/text-to-speech", body,
                       {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    task_id = created.get("task_id")
    if not task_id:
        raise RuntimeError(f"AI33 create failed: {created}")
    log(f"  AI33 task {task_id} ({voice})")
    for _ in range(200):
        task = _request("GET", f"/v1/task/{task_id}")
        task = task.get("data", task)
        if task.get("status") in ("done", "error"):
            break
        time.sleep(3)
    if task.get("status") != "done":
        raise RuntimeError(f"AI33 task failed: {json.dumps(task)[:600]}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "voice.task.json").write_text(json.dumps(task, indent=2))
    meta = task["metadata"]
    download(meta["audio_url"], folder / "voice.mp3")
    if meta.get("json_url"):
        download(meta["json_url"], folder / "voice.timing.json")
    if meta.get("srt_url"):
        download(meta["srt_url"], folder / "voice.srt")
    return folder / "voice.mp3"
