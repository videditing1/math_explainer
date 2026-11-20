"""Sync animation beats to narration words.

A VoiceScene reads `voice.timing.json` (per-word timings from AI33) that sits next to the
scene file. Before a voice exists it estimates timings from `script.txt` at ~165 wpm, so
you can draft the animation first and the real timings slot in later.

    class Main(VoiceScene):
        def construct(self):
            self.play_at("how", Write(title))                 # starts on the word "how"
            self.play_until("pairs", Create(web))             # finishes as "pairs" is said
            self.play_at("two hundred", FadeIn(counter))      # phrases work too
            self.play_at("match", Flash(dot), nth=2)          # 2nd occurrence
            self.hold_end()                                   # hold after the last word
"""
from __future__ import annotations

import inspect
import json
import pathlib
import re

from manim import Scene

WPM_ESTIMATE = 165


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load_words(folder: pathlib.Path) -> tuple[list[dict], bool]:
    """Returns (words, is_real_timing). Each word: {text, start, end}."""
    timing = folder / "voice.timing.json"
    if timing.exists():
        data = json.loads(timing.read_text())
        words = [w for seg in data for w in seg["words"] if w.get("type", "word") == "word"]
        return words, True
    script = folder / "script.txt"
    toks = script.read_text().split() if script.exists() else []
    step = 60 / WPM_ESTIMATE
    words = []
    for i, tok in enumerate(toks):
        pause = 0.35 * sum(1 for w in toks[:i] if w[-1] in ".?!")
        words.append({"text": tok, "start": 0.2 + i * step + pause,
                      "end": 0.2 + (i + 1) * step + pause})
    return words, False


class VoiceScene(Scene):
    """Scene whose timeline is driven by narration word timings."""

    #: embed voice.mp3 in renders so previews have narration (final mix replaces it)
    embed_voice = True

    def setup(self):
        self.folder = pathlib.Path(inspect.getfile(type(self))).resolve().parent
        self.words, self.real_timing = load_words(self.folder)
        voice = self.folder / "voice.mp3"
        if self.embed_voice and self.real_timing and voice.exists():
            self.add_sound(str(voice))

    # --- timeline helpers -----------------------------------------------------------
    @property
    def now(self) -> float:
        return self.renderer.time

    def cue(self, phrase: str, nth: int = 1, end: bool = False) -> float:
        """Start (or end) time of the nth occurrence of a word or phrase in the narration."""
        target = [_norm(t) for t in phrase.split()]
        toks = [_norm(w["text"]) for w in self.words]
        hits = [i for i in range(len(toks) - len(target) + 1)
                if toks[i:i + len(target)] == target]
        if len(hits) < nth:
            raise KeyError(f"cue {phrase!r} #{nth} not in narration "
                           f"(found {len(hits)}). Words: {' '.join(w['text'] for w in self.words)}")
        i = hits[nth - 1]
        return self.words[i + len(target) - 1]["end"] if end else self.words[i]["start"]

    @property
    def narration_end(self) -> float:
        return self.words[-1]["end"] if self.words else 0.0

    def wait_until(self, t: float):
        if t - self.now > 1 / 60:
            self.wait(t - self.now)

    def play_at(self, phrase: str, *anims, nth: int = 1, lead: float = 0.0, **kw):
        """Wait for the word, then play (starting `lead` seconds early)."""
        self.wait_until(self.cue(phrase, nth) - lead)
        self.play(*anims, **kw)

    def play_until(self, phrase: str, *anims, nth: int = 1, end: bool = False,
                   min_time: float = 0.3, **kw):
        """Play now, timed to finish exactly as the word starts (or ends, with end=True)."""
        rt = max(min_time, self.cue(phrase, nth, end) - self.now)
        self.play(*anims, run_time=rt, **kw)

    def hold_end(self, extra: float = 1.4):
        """Hold the payoff frame after the last word."""
        self.wait_until(self.narration_end + extra)
