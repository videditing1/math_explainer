"""The "winding machine" from 'But what is the Fourier Transform?', rebuilt from scratch.

Three linked views driven by ONE ValueTracker (the winding frequency):
  1. the signal g(t) on top,
  2. the signal wrapped around a circle, with its centre of mass,
  3. the x-coordinate of that centre of mass plotted against winding frequency.

Render:  manim -pql winding_machine.py WindingMachine      (fast preview)
         manim -pqh winding_machine.py WindingMachine      (1080p60 final)
"""
import numpy as np

from explainer import *

T_MAX = 4.5                     # seconds of signal we look at
SIGNAL_FREQS = (2, 3)           # beats per second; try (3,) first, then (2, 3)
SAMPLES = np.linspace(0, T_MAX, 1500)


def g(t):
    """Shifted-up cosines, so the wrapped graph is always 'radius >= 0'."""
    return sum(0.5 * (np.cos(TAU * f * t) + 1) for f in SIGNAL_FREQS) / len(SIGNAL_FREQS)


def centre_of_mass(f):
    z = g(SAMPLES) * np.exp(-TAU * 1j * f * SAMPLES)
    return z.mean()


class WindingMachine(Scene):
    def construct(self):
        freq = ValueTracker(0.3)

        # 1. signal graph ---------------------------------------------------------
        top = numbered_axes([0, T_MAX, 1], [0, 1, 0.5], x_length=11, y_length=1.6)
        top.to_edge(UP, buff=0.4)
        signal = top.plot(g, x_range=[0, T_MAX, 0.005], color=SIGNAL)
        top_lbl = label("Intensity").next_to(top.y_axis, UP, buff=0.1)
        # vertical ticks every full rotation, re-drawn as the frequency changes
        rotation_marks = always_redraw(lambda: VGroup(*[
            DashedLine(top.c2p(k / freq.get_value(), 0), top.c2p(k / freq.get_value(), 1),
                       color=WHITE, stroke_width=1.5, dash_length=0.06)
            for k in range(1, int(T_MAX * freq.get_value()) + 1)
        ]))

        # 2. wound-up graph -------------------------------------------------------
        plane = NumberPlane(x_range=[-1.2, 1.2, 0.5], y_range=[-1.2, 1.2, 0.5],
                            x_length=3.6, y_length=3.6,
                            background_line_style={"stroke_color": GRID, "stroke_width": 1})
        plane.to_corner(DL, buff=0.5)
        unit = Circle(radius=plane.x_length / 2.4, color=MUTED, stroke_width=1).move_to(plane.c2p(0, 0))
        unit.set_stroke(opacity=0.5)

        def wound():
            f = freq.get_value()
            z = g(SAMPLES) * np.exp(-TAU * 1j * f * SAMPLES)
            pts = [plane.c2p(p.real, p.imag) for p in z]
            return VMobject(color=SIGNAL, stroke_width=2).set_points_smoothly(pts[::3])

        wound_graph = always_redraw(wound)
        com_dot = always_redraw(lambda: Dot(
            plane.c2p(centre_of_mass(freq.get_value()).real, centre_of_mass(freq.get_value()).imag),
            color=MASS, radius=0.07))
        freq_readout = always_redraw(lambda: label(
            f"{freq.get_value():.2f} cycles/second", color=WHITE
        ).next_to(plane, UP, buff=0.15))

        # 3. "almost Fourier transform" ---------------------------------------------
        right = numbered_axes([0, 5, 1], [-0.5, 1, 0.5], color=FREQ, x_length=6.2, y_length=3.2)
        right.to_corner(DR, buff=0.5)
        right_lbl = label("x-coordinate of centre of mass", color=MASS).next_to(right, UP, buff=0.1)
        x_lbl = label("Frequency").next_to(right.x_axis, DOWN, buff=0.35).align_to(right, RIGHT)
        transform_curve = always_redraw(lambda: right.plot(
            lambda f: centre_of_mass(f).real, x_range=[0.01, max(freq.get_value(), 0.02), 0.01],
            color=MASS))

        # --- choreography --------------------------------------------------------------
        self.play(Create(top), FadeIn(top_lbl), Create(signal, run_time=2))
        self.wait(0.5)
        self.play(FadeIn(plane), Create(unit), FadeIn(freq_readout))
        # the key "aha": literally move the graph from line to circle
        self.play(ReplacementTransform(signal.copy(), wound_graph), run_time=2)
        self.add(rotation_marks)
        self.play(freq.animate.set_value(1.0), run_time=3, rate_func=smooth)
        self.wait()
        self.play(FadeIn(com_dot, scale=0.5))
        self.play(Create(right), FadeIn(right_lbl), FadeIn(x_lbl))
        self.add(transform_curve)
        # sweep: slow down near the signal frequencies so the eye catches the spikes
        self.play(freq.animate.set_value(0.01), run_time=1.5)
        for target, rt in [(1.7, 4), (2.3, 4), (2.7, 2.5), (3.3, 4), (5.0, 4)]:
            self.play(freq.animate.set_value(target), run_time=rt, rate_func=linear)
        self.wait()
        # land on a peak and hold - the payoff frame
        self.play(freq.animate.set_value(3.0), run_time=3)
        self.play(Indicate(com_dot, color=HILITE, scale_factor=2))
        self.wait(2)
