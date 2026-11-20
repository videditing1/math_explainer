"""Minimal client for the Epidemic Sound MCP server (music search + download).

    python tools/epidemic.py tools                       # list tools
    python tools/epidemic.py schema SearchRecordings      # show a tool's input schema
    python tools/epidemic.py call SearchRecordings '{"query": "calm curious piano", "first": 10}'

Needs EPIDEMIC_SOUND_MCP_API_KEY (an MCP Server key from Account → API keys) in env or .env.
Requires an active Epidemic Sound subscription; downloads are licensed to that account.
"""
import json
import os
import pathlib
import sys
import urllib.request

URL = "https://www.epidemicsound.com/a/mcp-service/mcp"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _key():
    if os.environ.get("EPIDEMIC_SOUND_MCP_API_KEY"):
        return os.environ["EPIDEMIC_SOUND_MCP_API_KEY"]
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("EPIDEMIC_SOUND_MCP_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("EPIDEMIC_SOUND_MCP_API_KEY not set")


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
