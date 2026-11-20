"""House style shared by every scene: a 3b1b-like look built from Manim CE defaults.

Import with `from style import *` from inside the scenes/ folder.
"""
import shutil

import numpy as np

from manim import *

# --- Palette -------------------------------------------------------------------
# Black background, one "hero" colour per concept, colours stay consistent for the
# whole video (if frequency is yellow at 0:30 it is yellow at 18:00).
BG = "#000000"
SIGNAL = YELLOW          # the thing being studied (the signal / the drawing)
FREQ = TEAL              # frequency / axis accents
MASS = RED               # derived quantity (centre of mass, coefficient)
HILITE = PINK            # "look here" highlight
GRID = BLUE_E            # faint background grid
MUTED = GREY_B

config.background_color = BG

HAS_LATEX = shutil.which("latex") is not None and shutil.which("dvisvgm") is not None


def eq(tex: str, plain: str | None = None, **kw) -> Mobject:
    """MathTex when LaTeX is installed, otherwise a readable Text fallback.

    Real productions should install LaTeX (see docs/02-toolchain.md); the fallback just
    lets the examples render on a bare machine.
    """
    if HAS_LATEX:
        return MathTex(tex, **kw)
    kw.pop("tex_to_color_map", None)
    return Text(plain or tex, font="Georgia", slant=ITALIC, **kw).scale(0.6)


def numbered_axes(x_range, y_range, color=MUTED, **kw) -> Axes:
    """Axes with tick numbers. Uses Manim's (LaTeX) numbers when possible, else Text."""
    ax = Axes(x_range=x_range, y_range=y_range, tips=False,
              axis_config={"color": color, "include_numbers": HAS_LATEX, "font_size": 20}, **kw)
    if not HAS_LATEX:
        for v in np.arange(x_range[0] + x_range[2], x_range[1] + 1e-9, x_range[2]):
            ax.add(Text(f"{v:g}", font="Georgia", font_size=16).next_to(ax.c2p(v, y_range[0]), DOWN, 0.12))
        for v in np.arange(y_range[0], y_range[1] + 1e-9, y_range[2]):
            ax.add(Text(f"{v:g}", font="Georgia", font_size=16).next_to(ax.c2p(x_range[0], v), LEFT, 0.12))
    return ax


def label(text: str, **kw) -> Text:
    """Small serif label, the Computer-Modern-ish look 3b1b uses for axis labels."""
    kw.setdefault("font", "Georgia")
    return Text(text, **kw).scale(0.45)
