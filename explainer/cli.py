"""`explainer`: one command line for the whole pipeline.

    explainer doctor                  check tools, keys and credits
    explainer new <slug>              scaffold videos/<slug>/ (script, scene, config)
    explainer voice <slug>            narration + word timings via AI33   (skips if present)
    explainer music <slug>            pick + download a steady music bed (skips if present)
    explainer render <slug> [--hq]    render the Manim scene (480p15 draft, or 1080p60)
    explainer mix <slug>              voice + ducked music -> videos/<slug>/<slug>_final.mp4
    explainer build <slug> [--hq]     all of the above in order
    explainer voices                  list available narrator voices
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import statistics
import subprocess
import sys
import tempfile
import tomllib
import urllib.request

from .env import MEDIA, ROOT, VIDEOS, get_key

QUALITY = {"draft": ("-ql", "480p15"), "hq": ("-qh", "1080p60"), "4k": ("-qk", "2160p60")}


# --- helpers ------------------------------------------------------------------------
def say(msg):
    print(f"\033[36m›\033[0m {msg}", flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def folder(slug: str) -> pathlib.Path:
    f = VIDEOS / slug
    if not f.exists():
        raise SystemExit(f"no such video: {f} (create it with `explainer new {slug}`)")
    return f


def config(slug: str) -> dict:
    cfg = {"title": slug, "scene": "Main", "voice": {"name": "george", "speed": 1.0},
           "music": {"query": "gentle curious piano documentary", "volume": 0.22}}
    path = folder(slug) / "video.toml"
    if path.exists():
        user = tomllib.loads(path.read_text())
        for k, v in user.items():
            cfg[k] = {**cfg[k], **v} if isinstance(v, dict) and isinstance(cfg.get(k), dict) else v
    return cfg


def duration(path: pathlib.Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def mean_volume(path, start, length=5.0) -> float:
    out = subprocess.run(["ffmpeg", "-ss", str(start), "-t", str(length), "-i", str(path),
                          "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    for line in out.stderr.splitlines():
        if "mean_volume" in line:
            return float(line.split(":")[1].split()[0])
    return -91.0


# --- commands -----------------------------------------------------------------------
def cmd_doctor(a):
    ok = True

    def check(name, cond, fix=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'✓' if cond else '✗'} {name}" + ("" if cond else f"   → {fix}"))

    print("Tools")
    check("ffmpeg", shutil.which("ffmpeg"), "brew install ffmpeg")
    check("manim", shutil.which("manim") or (ROOT / ".venv/bin/manim").exists(), "./setup.sh")
    check("cairo/pango", shutil.which("pkg-config") and subprocess.run(
        ["pkg-config", "--exists", "pangocairo"]).returncode == 0, "brew install cairo pango pkg-config")
    has_latex = shutil.which("latex") and shutil.which("dvisvgm")
    print(f"  {'✓' if has_latex else '~'} LaTeX" + ("" if has_latex else
          "   → optional but needed for real maths typesetting: brew install --cask mactex-no-gui"))
    print("Keys (.env)")
    for k in ("AI33_API_KEY", "EPIDEMIC_SOUND_MCP_API_KEY"):
        check(k, get_key(k, required=False), f"add {k}=... to .env")
    if get_key("AI33_API_KEY", required=False):
        try:
            from . import ai33
            print(f"  ✓ AI33 credits: {ai33.credits():,}")
        except Exception as e:  # noqa: BLE001
            check("AI33 reachable", False, str(e)[:120])
    if get_key("EPIDEMIC_SOUND_MCP_API_KEY", required=False):
        try:
            from .epidemic import Client
            Client()
            print("  ✓ Epidemic Sound MCP reachable")
        except Exception as e:  # noqa: BLE001
            check("Epidemic Sound reachable", False, str(e)[:120])
    print("All good." if ok else "Fix the ✗ items above.")


def cmd_new(a):
    dest = VIDEOS / a.slug
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    shutil.copytree(ROOT / "explainer" / "template", dest)
    cfg = (dest / "video.toml").read_text().replace("{{title}}", a.title or a.slug.replace("_", " ").title())
    (dest / "video.toml").write_text(cfg)
    say(f"created {dest.relative_to(ROOT)}/")
    print("  1. write the narration in script.txt (use beats.md as the outline)\n"
          f"  2. draft the animation in scene.py, then: explainer render {a.slug}\n"
          f"  3. explainer build {a.slug} --hq")


def cmd_voices(a):
    from . import ai33
    for v in ai33.voices():
        lab = v.get("labels") or {}
        print(f"elevenlabs_{v['voice_id']}  {v['name']:<42} {lab.get('accent','')}")
    print("\nShort names:", ", ".join(ai33.VOICES))


def cmd_voice(a):
    from . import ai33
    f, cfg = folder(a.slug), config(a.slug)
    if (f / "voice.mp3").exists() and not a.force:
        say("voice.mp3 exists, skipping (use --force to regenerate)")
        return
    text = (f / "script.txt").read_text().strip()
    say(f"generating narration ({len(text.split())} words, voice={cfg['voice']['name']})")
    ai33.synthesize(text, f, cfg["voice"]["name"], cfg["voice"]["speed"], log=print)
    say(f"voice: {duration(f / 'voice.mp3'):.1f}s, word timings saved")


def cmd_music(a):
    from . import epidemic
    f, cfg = folder(a.slug), config(a.slug)
    dest = f / "music.mp3"
    if dest.exists() and not a.force:
        say("music.mp3 exists, skipping (use --force to re-pick)")
        return
    need = (duration(f / "voice.mp3") if (f / "voice.mp3").exists() else 60) + 3
    track_id = a.id or cfg["music"].get("id")
    if track_id:
        meta = {"id": track_id}
    else:
        query = a.query or cfg["music"]["query"]
        say(f"searching Epidemic Sound: {query!r}")
        tracks = epidemic.search_tracks(query, min_s=int(need) + 10)
        # Score previews: we want a bed that is steady (low variance) and present from bar one.
        scored = []
        with tempfile.TemporaryDirectory() as tmp:
            for t in tracks[:8]:
                p = pathlib.Path(tmp) / f"{t['id']}.mp3"
                req = urllib.request.Request(t["preview"], headers={"User-Agent": "Mozilla/5.0"})
                p.write_bytes(urllib.request.urlopen(req, timeout=60).read())
                vols = [mean_volume(p, s) for s in range(0, int(need), 5)]
                score = statistics.pstdev(vols) + max(0, -30 - min(vols)) * 2
                scored.append((score, t, vols))
                print(f"    {score:5.2f}  {t['title']:<28} {' '.join(f'{v:5.1f}' for v in vols)}")
        score, meta, _ = min(scored, key=lambda s: s[0])
        say(f"picked {meta['title']!r}" + (f" by {meta['artist']}" if meta.get('artist') else "")
            + f" (steadiness score {score:.2f})")
    epidemic.download_track(meta["id"], dest)
    (f / "music.json").write_text(json.dumps(meta, indent=2))
    say(f"saved music.mp3 ({duration(dest):.0f}s); licence note in music.json")


def rendered_path(slug, scene, quality) -> pathlib.Path:
    return MEDIA / slug / "videos" / "scene" / QUALITY[quality][1] / f"{scene}.mp4"


def cmd_render(a):
    f, cfg = folder(a.slug), config(a.slug)
    q = "4k" if a.k4 else "hq" if a.hq else "draft"
    manim = shutil.which("manim") or str(ROOT / ".venv/bin/manim")
    say(f"rendering {cfg['scene']} at {QUALITY[q][1]}")
    run([manim, QUALITY[q][0], "--media_dir", str(MEDIA / a.slug), "scene.py", cfg["scene"]], cwd=f)
    out = rendered_path(a.slug, cfg["scene"], q)
    say(f"rendered {out.relative_to(ROOT)} ({duration(out):.1f}s)")
    return out


def cmd_mix(a):
    f, cfg = folder(a.slug), config(a.slug)
    q = "4k" if getattr(a, "k4", False) else "hq" if getattr(a, "hq", False) else None
    candidates = [rendered_path(a.slug, cfg["scene"], k) for k in ([q] if q else ["4k", "hq", "draft"])]
    video = next((c for c in candidates if c.exists()), None)
    if not video:
        raise SystemExit("nothing rendered yet: run `explainer render`")
    dur = duration(video)
    final = f / f"{a.slug}_final.mp4"
    inputs, chains = ["-i", str(video)], []
    has_voice, has_music = (f / "voice.mp3").exists(), (f / "music.mp3").exists()
    if has_voice:
        inputs += ["-i", str(f / "voice.mp3")]
        chains.append(f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,"
                      f"apad=whole_dur={dur},asplit=2[v][vsc]")
    if has_music:
        mi = 2 if has_voice else 1
        inputs += ["-i", str(f / "music.mp3")]
        vol = cfg["music"].get("volume", 0.22)
        chains.append(f"[{mi}:a]atrim=0:{dur},volume={vol},afade=t=in:d=1.5,"
                      f"afade=t=out:st={max(0, dur - 2.5)}:d=2.5,aresample=48000[m]")
    if has_voice and has_music:  # duck the music under the voice
        chains += ["[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=400[md]",
                   f"[v][md]amix=inputs=2:duration=longest:normalize=0,atrim=0:{dur}[a]"]
    elif has_voice:
        chains.append("[vsc]anullsink;[v]anull[a]")
    elif has_music:
        chains.append("[m]anull[a]")
    else:
        raise SystemExit("no voice.mp3 or music.mp3 to mix")
    say(f"mixing {video.relative_to(ROOT)} + {'voice ' if has_voice else ''}{'music' if has_music else ''}")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chains),
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(0, dur - 0.5)), "-i", str(final),
         "-frames:v", "1", str(f / "thumbnail.png")])
    say(f"final: {final.relative_to(ROOT)} ({duration(final):.1f}s) + thumbnail.png")


def cmd_build(a):
    a.force = False
    a.query = a.id = None
    if get_key("AI33_API_KEY", required=False):
        cmd_voice(a)
    if get_key("EPIDEMIC_SOUND_MCP_API_KEY", required=False):
        cmd_music(a)
    cmd_render(a)
    cmd_mix(a)


def main(argv=None):
    p = argparse.ArgumentParser(prog="explainer", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    sub.add_parser("voices").set_defaults(fn=cmd_voices)
    n = sub.add_parser("new")
    n.add_argument("slug")
    n.add_argument("--title")
    n.set_defaults(fn=cmd_new)
    for name, fn in [("voice", cmd_voice), ("music", cmd_music), ("render", cmd_render),
                     ("mix", cmd_mix), ("build", cmd_build)]:
        s = sub.add_parser(name)
        s.add_argument("slug")
        s.set_defaults(fn=fn)
        if name in ("voice", "music"):
            s.add_argument("--force", action="store_true")
        if name == "music":
            s.add_argument("--query")
            s.add_argument("--id", help="pin a specific Epidemic Sound track id")
        if name in ("render", "mix", "build"):
            s.add_argument("--hq", action="store_true", help="1080p60")
            s.add_argument("--4k", dest="k4", action="store_true", help="2160p60")
    a = p.parse_args(argv)
    try:
        a.fn(a)
    except subprocess.CalledProcessError as e:
        sys.exit(f"command failed: {' '.join(map(str, e.cmd))[:200]}")


if __name__ == "__main__":
    main()
