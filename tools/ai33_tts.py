"""Generate narration with AI33 / OpenSpeaker (ElevenLabs voices) and save audio + word timings.

Usage:
    python tools/ai33_tts.py demos/birthday_paradox/script.txt demos/birthday_paradox/voice
        [--voice elevenlabs_JBFqnCBsd6RMkjVDRZzb] [--speed 1.0]

Writes <out>.mp3 and <out>.task.json (raw task, including any transcript/timing data).
Needs AI33_API_KEY in the environment or in the repo's .env file.

API notes (from the docs built into the ai33.pro web app):
  POST /v3/text-to-speech  multipart: text, voice_id (provider-prefixed), speed, with_transcript
  -> {success, task_id};  poll GET /v1/task/{id} until status == "done" | "error".
  GET /v1/credits shows the balance;  GET /v2/voices lists ElevenLabs voice ids.
"""
import argparse
import json
import os
import pathlib
import sys
import time
import urllib.request
import uuid

BASE = "https://api.ai33.pro"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def api_key() -> str:
    if os.environ.get("AI33_API_KEY"):
        return os.environ["AI33_API_KEY"]
    env = ROOT / ".env"
    for line in env.read_text().splitlines() if env.exists() else []:
        if line.startswith("AI33_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("AI33_API_KEY not set (put it in .env)")


def request(method, path, data=None, headers=None):
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"xi-api-key": api_key(), **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def multipart(fields: dict) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    body = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, v in fields.items()) + f"--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def find_audio_url(obj):
    """The task metadata layout isn't documented for TTS; find the first audio-looking URL."""
    if isinstance(obj, str):
        return obj if obj.startswith("http") and any(x in obj for x in (".mp3", ".wav", "audio")) else None
    if isinstance(obj, dict):
        obj = list(obj.values())
    if isinstance(obj, list):
        for v in obj:
            if (u := find_audio_url(v)):
                return u
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("out", help="output path without extension")
    ap.add_argument("--voice", default="elevenlabs_JBFqnCBsd6RMkjVDRZzb")  # George: warm storyteller
    ap.add_argument("--speed", default="1.0")
    a = ap.parse_args()

    text = pathlib.Path(a.script).read_text().strip()
    body, ctype = multipart({"text": text, "voice_id": a.voice, "speed": a.speed,
                             "with_transcript": "true"})
    created = request("POST", "/v3/text-to-speech", body, {"Content-Type": ctype})
    task_id = created.get("task_id") or sys.exit(f"create failed: {created}")
    print("task", task_id)

    for _ in range(120):
        task = request("GET", f"/v1/task/{task_id}")
        task = task.get("data", task)
        if task.get("status") in ("done", "error"):
            break
        time.sleep(3)
    if task.get("status") != "done":
        sys.exit(f"task failed: {json.dumps(task)[:800]}")

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".task.json").write_text(json.dumps(task, indent=2))
    meta = task.get("metadata", {})
    url = meta.get("audio_url") or find_audio_url(meta)
    if not url:
        sys.exit("done, but no audio URL found; inspect " + str(out.with_suffix(".task.json")))
    download(url, out.with_suffix(".mp3"))
    # word/segment timings, used to sync animation beats to the narration
    for key, ext in (("json_url", ".timing.json"), ("srt_url", ".srt")):
        if meta.get(key):
            download(meta[key], out.with_suffix(ext))


def download(url, dest):
    # the CDN rejects Python's default User-Agent
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        pathlib.Path(dest).write_bytes(r.read())
    print("saved", dest)


if __name__ == "__main__":
    main()
