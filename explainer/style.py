"""House style: a 3b1b-like look built on Manim CE.

Rules (also in CLAUDE.md):
  * pure black background, faint blue grid, thin strokes
  * one colour = one concept, for the whole video
  * serif text (Georgia) for words; LaTeX (Computer Modern) for maths when installed
"""
import os
import shutil

import numpy as np
from manim import *

# macOS TeX (BasicTeX/MacTeX) lives here; add it even if this shell started before the install
_TEXBIN = "/Library/TeX/texbin"
if os.path.isdir(_TEXBIN) and _TEXBIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _TEXBIN + os.pathsep + os.environ.get("PATH", "")

# --- Palette: semantic names, not colours. Pick per video, keep consistent. -------
BG = "#000000"
SUBJECT = YELLOW         # the thing being studied (signal, people, the drawing)
SECONDARY = TEAL         # axes accents / a second quantity / curves
DERIVED = RED            # a derived quantity (centre of mass, a match, an answer)
HILITE = PINK            # "look here", the viewer's own perspective ("you")
STRUCTURE = BLUE_C       # connective tissue: chords, grid, construction lines
MUTED = GREY_B           # labels, axes, de-emphasised guesses
GRID = BLUE_E

# backwards-compatible names used by the example scenes
SIGNAL, FREQ, MASS = SUBJECT, SECONDARY, DERIVED

FONT = "Georgia"
config.background_color = BG

HAS_LATEX = shutil.which("latex") is not None and shutil.which("dvisvgm") is not None


def T(text: str, size: float = 36, color=WHITE, **kw) -> Text:
    """House text: serif, sized in points."""
    return Text(text, font=FONT, font_size=size, color=color, **kw)


def label(text: str, **kw) -> Text:
    """Small serif label (axis labels, annotations)."""
    kw.setdefault("font", FONT)
    return Text(text, **kw).scale(0.45)


def eq(tex: str, plain: str | None = None, size: float = 40, **kw) -> Mobject:
    """Maths. MathTex when LaTeX is installed, otherwise a readable serif fallback.

    Always pass `plain` (unicode version) so drafts render on machines without LaTeX:
        eq(r"\\left(\\tfrac{364}{365}\\right)^{253}", "(364/365)²⁵³")
    """
    if HAS_LATEX:
        return MathTex(tex, font_size=size, **kw)
    kw.pop("tex_to_color_map", None)
    return Text(plain or tex, font=FONT, font_size=size * 0.75, **kw)


def numbered_axes(x_range, y_range, color=MUTED, number_size=16, **kw) -> Axes:
    """Axes with tick numbers; LaTeX numbers when possible, serif Text otherwise."""
    ax = Axes(x_range=x_range, y_range=y_range, tips=False,
              axis_config={"color": color, "include_numbers": HAS_LATEX, "font_size": 20}, **kw)
    if not HAS_LATEX:
        for v in np.arange(x_range[0] + x_range[2], x_range[1] + 1e-9, x_range[2]):
            ax.add(T(f"{v:g}", number_size).next_to(ax.c2p(v, y_range[0]), DOWN, 0.12))
        for v in np.arange(y_range[0], y_range[1] + 1e-9, y_range[2]):
            ax.add(T(f"{v:g}", number_size).next_to(ax.c2p(x_range[0], v), LEFT, 0.12))
    return ax
