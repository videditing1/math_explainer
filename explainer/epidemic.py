"""Minimal client for the Epidemic Sound MCP server (music search + download).

    python -m explainer.epidemic tools                       # list tools
    python -m explainer.epidemic schema SearchRecordings      # show a tool's input schema
    python -m explainer.epidemic call SearchRecordings '{"query": {"term": "calm piano"}, "first": 10}'
Higher-level helpers: search_tracks(), download_track(); `explainer music` picks automatically.

Needs EPIDEMIC_SOUND_MCP_API_KEY (an MCP Server key from Account → API keys) in env or .env.
Requires an active Epidemic Sound subscription; downloads are licensed to that account.
"""
import json
import pathlib
import re
import sys
import urllib.request

from .env import get_key

URL = "https://www.epidemicsound.com/a/mcp-service/mcp"


def _key():
    return get_key("EPIDEMIC_SOUND_MCP_API_KEY")


class Client:
    def __init__(self):
        self.sid = None
        self.n = 0
        res, hdrs = self._post({"jsonrpc": "2.0", "id": self._id(), "method": "initialize",
                                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                           "clientInfo": {"name": "math-explainer", "version": "1"}}})
        self.sid = hdrs.get("mcp-session-id")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _id(self):
        self.n += 1
        return self.n

    def _post(self, payload):
        h = {"Authorization": f"Bearer {_key()}", "Content-Type": "application/json",
             "Accept": "application/json, text/event-stream", "mcp-protocol-version": "2025-06-18"}
        if self.sid:
            h["mcp-session-id"] = self.sid
        req = urllib.request.Request(URL, json.dumps(payload).encode(), h, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read().decode()
            hdrs = {k.lower(): v for k, v in r.headers.items()}
        msgs = [json.loads(l[5:]) for l in body.splitlines() if l.startswith("data:") and l[5:].strip()]
        if not msgs and body.strip().startswith("{"):
            msgs = [json.loads(body)]
        return (msgs[-1] if msgs else None), hdrs

    def list_tools(self):
        return self._post({"jsonrpc": "2.0", "id": self._id(), "method": "tools/list"})[0]["result"]["tools"]

    def call(self, name, args):
        res = self._post({"jsonrpc": "2.0", "id": self._id(), "method": "tools/call",
                          "params": {"name": name, "arguments": args}})[0]
        if "error" in res:
            raise RuntimeError(res["error"])
        out = res["result"]
        if out.get("structuredContent") is not None:
            return out["structuredContent"]
        text = "".join(c.get("text", "") for c in out.get("content", []))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text


def _walk(o):
    if isinstance(o, dict):
        if "title" in o and "audioFile" in o:
            yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def search_tracks(term: str, min_s: int = 40, max_s: int = 300, first: int = 12) -> list[dict]:
    """[{id, title, artist, duration_s, bpm, preview}] for a music search."""
    res = Client().call("SearchRecordings", {
        "query": {"term": term},
        "filter": {"duration": {"min": min_s * 1000, "max": max_s * 1000}}, "first": first})
    out = []
    for r in _walk(res):
        credits = r.get("credits") or []
        artist = next((c["artist"]["name"] for c in credits
                       if isinstance(c, dict) and c.get("artist")), None)
        out.append({"id": r["id"], "title": r["title"], "artist": artist, "bpm": r.get("bpm"),
                    "duration_s": r["audioFile"]["durationInMilliseconds"] / 1000,
                    "preview": r["audioFile"]["lqmp3Url"]})
    return out


def download_track(track_id: str, dest: pathlib.Path) -> pathlib.Path:
    """Download the full-quality licensed MP3 (needs an active subscription)."""
    res = Client().call("DownloadRecording", {"id": track_id,
                                              "options": {"fileType": "MP3", "stemType": "FULL"}})
    url = re.findall(r'https://[^"\\ ]+', json.dumps(res))[0]
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        dest.write_bytes(r.read())
    return dest


if __name__ == "__main__":
    c = Client()
    cmd = sys.argv[1]
    if cmd == "tools":
        for t in c.list_tools():
            print(t["name"])
    elif cmd == "schema":
        t = next(t for t in c.list_tools() if t["name"] == sys.argv[2])
        print(json.dumps(t["inputSchema"], indent=1))
    elif cmd == "call":
        print(json.dumps(c.call(sys.argv[2], json.loads(sys.argv[3])), indent=1))
