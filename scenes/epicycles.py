"""Drawing with rotating vectors (complex Fourier series), rebuilt from scratch.

    c_n = ∫_0^1 f(t) e^{-2πint} dt          (computed numerically below)
    f(t) ≈ Σ c_n e^{2πint},  n = -N..N      (drawn as arrows tip-to-tail)

Any closed path works. Pass an SVG to draw anything:
    PATH_SVG=my_logo.svg manim -pql epicycles.py Epicycles
Without one it draws a built-in trefoil-heart curve.
"""
import os

import numpy as np

from explainer import *

N_VECTORS = 51            # odd: frequencies -25..25
CYCLE_SECONDS = 12        # how long one full trace takes on screen
SAMPLES = 2000


def path_points() -> np.ndarray:
    """Sample the target drawing as complex numbers z(t), t in [0,1)."""
    svg = os.environ.get("PATH_SVG")
    ts = np.linspace(0, 1, SAMPLES, endpoint=False)
    if svg:
        mob = SVGMobject(svg).family_members_with_points()[0]
        mob.set_height(5)
        pts = np.array([mob.point_from_proportion(t) for t in ts])
        pts -= pts.mean(axis=0)
        return pts[:, 0] + 1j * pts[:, 1]
    # default: a heart, a curve with sharp-ish corners so many terms matter
    s = TAU * ts
    x = 16 * np.sin(s) ** 3
    y = 13 * np.cos(s) - 5 * np.cos(2 * s) - 2 * np.cos(3 * s) - np.cos(4 * s)
    return (x + 1j * y) / 6


def coefficients(z: np.ndarray, n_vec: int):
    """Numerical integral: average of z(t) * e^{-2πint}. Returns (n, c_n) sorted by |c_n|."""
    ts = np.linspace(0, 1, len(z), endpoint=False)
    half = n_vec // 2
    ns = np.arange(-half, half + 1)
    cs = np.array([(z * np.exp(-TAU * 1j * n * ts)).mean() for n in ns])
    order = np.argsort(-np.abs(cs))  # biggest arrows first, like the video
    return ns[order], cs[order]


class Epicycles(Scene):
    def construct(self):
        ns, cs = coefficients(path_points(), N_VECTORS)
        t = ValueTracker(0)

        def tips(time):
            pos = [0j]
            for n, c in zip(ns, cs):
                pos.append(pos[-1] + c * np.exp(TAU * 1j * n * time))
            return pos

        def to_point(z):
            return np.array([z.real, z.imag, 0])

        def vectors():
            p = tips(t.get_value())
            grp = VGroup()
            for i in range(len(p) - 1):
                a, b = to_point(p[i]), to_point(p[i + 1])
                r = abs(p[i + 1] - p[i])
                if r < 1e-3:
                    continue
                grp.add(Circle(radius=r, stroke_width=1, color=BLUE_D)
                        .set_stroke(opacity=0.35).move_to(a))
                grp.add(Arrow(a, b, buff=0, stroke_width=2, color=WHITE,
                              max_tip_length_to_length_ratio=0.12, tip_length=0.15))
            return grp

        arrows = always_redraw(vectors)
        trace = TracedPath(lambda: to_point(tips(t.get_value())[-1]),
                           stroke_color=SIGNAL, stroke_width=3)

        title = label("Complex Fourier series", color=WHITE).scale(1.4).to_corner(UL)
        formula = eq(r"c_n = \int_0^1 f(t)\, e^{-2\pi i n t}\, dt",
                     "c_n = ∫ f(t) e^(-2πint) dt").to_corner(UR)

        self.play(FadeIn(title))
        self.add(arrows, trace)
        self.play(t.animate.set_value(1), run_time=CYCLE_SECONDS, rate_func=linear)
        self.play(FadeIn(formula, shift=DOWN * 0.3))
        self.wait()
