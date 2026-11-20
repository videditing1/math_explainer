"""Reusable building blocks for the house style."""
from manim import *

from .style import MUTED, T


def counter(tracker: ValueTracker, fmt: str = "{:.0f}", size: float = 40, color=WHITE,
            place=lambda m: m) -> Mobject:
    """Live number readout ("253 pairs", "2.00 cycles/second") without needing LaTeX.

        n = ValueTracker(0)
        c = counter(n, "{:.0f} pairs", place=lambda m: m.to_corner(DR))
        self.add(c); self.play(n.animate.set_value(253))
    """
    return always_redraw(lambda: place(T(fmt.format(tracker.get_value()), size, color)))


def title_card(text: str, size: float = 40) -> Text:
    """Question/title at the top of frame."""
    return T(text, size).to_edge(UP, buff=0.45)


def crossed(mob: Mobject, color=RED) -> Cross:
    """A red cross over a wrong guess."""
    return Cross(mob, stroke_color=color, stroke_width=6)


def callout(target: Mobject, text: str, color=YELLOW, direction=RIGHT, size: float = 26) -> VGroup:
    """Circle + short label pointing at something ("match!")."""
    ring = Circle(radius=max(target.width, target.height) / 2 + 0.15,
                  color=color, stroke_width=4).move_to(target)
    return VGroup(ring, T(text, size, color).next_to(ring, direction, buff=0.1))


def dim_except(scene: Scene, *keep: Mobject, opacity: float = 0.2, run_time: float = 0.6):
    """Fade everything but `keep` so the eye goes where the narration is."""
    others = [m for m in scene.mobjects if m not in keep]
    scene.play(*[m.animate.set_opacity(opacity) for m in others], run_time=run_time)


def axis_labels(ax: Axes, x: str, y: str, size: float = 22) -> VGroup:
    return VGroup(T(x, size, MUTED).next_to(ax.x_axis, DOWN, buff=0.45),
                  T(y, size, MUTED).next_to(ax.y_axis, UP, buff=0.15).align_to(ax, LEFT))
