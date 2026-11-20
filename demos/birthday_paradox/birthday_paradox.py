"""30-second demo: the birthday paradox.

Every animation beat is pinned to a word in the narration, using the per-word timings
that AI33 returns (voice.timing.json). Change the script, regenerate the voice, and the
beats re-sync automatically.

    cd demos/birthday_paradox
    ../../.venv/bin/manim -qh birthday_paradox.py BirthdayParadox
    ./mix.sh            # adds voice + music -> birthday_paradox_final.mp4
"""
import json
import math
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scenes"))
from style import *  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
WORDS = [w for w in json.loads((HERE / "voice.timing.json").read_text())[0]["words"]
         if w["type"] == "word"]

PEOPLE_COL = YELLOW
CHORD_COL = BLUE_C
YOU_COL = PINK
MATCH_COL = RED
CURVE_COL = TEAL


def cue(word: str, nth: int = 1) -> float:
    """Start time (s) of the nth occurrence of `word` in the narration."""
    hits = [w["start"] for w in WORDS
            if re.sub(r"[^a-z]", "", w["text"].lower()) == word]
    return hits[nth - 1]


def p_match(n: float) -> float:
    """P(at least one shared birthday among n people); smooth in n via log-gamma."""
    log_none = math.lgamma(366) - math.lgamma(366 - n) - n * math.log(365)
    return 1 - math.exp(log_none)


def T(text, size=36, color=WHITE, **kw):
    return Text(text, font="Georgia", font_size=size, color=color, **kw)


class BirthdayParadox(Scene):
    def wait_until(self, t: float):
        dt = t - self.renderer.time
        if dt > 1 / 60:
            self.wait(dt)

    def construct(self):
        # --- the year ring --------------------------------------------------------
        R = 2.45
        centre = DOWN * 0.35

        def day_point(d, r=R):
            a = PI / 2 - TAU * d / 365
            return centre + r * np.array([math.cos(a), math.sin(a), 0])

        ring = Circle(radius=R, color=GREY_B, stroke_width=2).move_to(centre)
        ticks = VGroup(*[Line(day_point(d, R - 0.08), day_point(d, R + 0.08),
                              stroke_width=1.5, color=GREY_B)
                         for d in np.linspace(0, 365, 12, endpoint=False)])
        months = VGroup(*[T(m, 18, GREY_B).move_to(day_point(d + 15, R + 0.35))
                          for m, d in zip("JFMAMJJASOND", np.linspace(0, 365, 12, endpoint=False))])
        year = VGroup(ring, ticks, months)

        title = T("How many people until two share a birthday?", 40).to_edge(UP, buff=0.45)

        # 23 birthdays, with one genuine shared day (that's the point)
        rng = np.random.default_rng(7)
        days = list(rng.choice(365, 22, replace=False))
        days.append(days[9])  # person 23 shares a birthday with person 10
        pts = [day_point(d) if i < 22 else day_point(d, R + 0.2) for i, d in enumerate(days)]
        dots = VGroup(*[Dot(p, radius=0.075, color=PEOPLE_COL) for p in pts])

        # B1: the question ----------------------------------------------------------
        self.wait_until(cue("how"))
        self.play(Write(title, run_time=1.6), Create(year, run_time=2.4, lag_ratio=0.1))

        # B2: the intuitive guess -----------------------------------------------------
        self.wait_until(cue("gut"))
        half = Arc(radius=R, start_angle=PI / 2, angle=-PI, color=GREY_C, stroke_width=8,
                   arc_center=centre).set_stroke(opacity=0.5)
        guess = T("180?", 96, GREY_B).move_to(centre)
        guess_note = T("gut instinct: about half the year", 20, GREY_B).next_to(guess, DOWN, buff=0.15)
        self.play(Create(half, run_time=1.4))
        self.wait_until(cue("one") - 0.1)
        self.play(FadeIn(guess, scale=1.2), FadeIn(guess_note, shift=UP * 0.2), run_time=0.7)

        # B3: the real answer -----------------------------------------------------------
        self.wait_until(cue("answer"))
        cross = Cross(guess, stroke_color=MATCH_COL, stroke_width=6)
        self.play(Create(cross), run_time=0.5)
        self.wait_until(cue("twenty") - 0.15)
        answer = T("23", 110, PEOPLE_COL).move_to(centre)
        self.play(FadeOut(VGroup(guess, guess_note, cross), run_time=0.3),
                  FadeOut(half, run_time=0.3),
                  FadeIn(answer, scale=0.6, run_time=0.5))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.12, run_time=1.0))

        # B4: not compared with *you* ----------------------------------------------------
        self.wait_until(cue("heres"))
        you = dots[0]
        you_lbl = T("you", 24, YOU_COL).next_to(you, UP + RIGHT, buff=0.08)
        self.play(answer.animate.scale(0.45).set_opacity(0.35), you.animate.set_color(YOU_COL),
                  FadeIn(you_lbl), run_time=0.6)
        yours = VGroup(*[Line(you.get_center(), d.get_center(), stroke_width=1.5, color=YOU_COL)
                         for d in dots[1:]])
        self.wait_until(cue("not"))
        self.play(LaggedStart(*[Create(l) for l in yours], lag_ratio=0.05, run_time=1.3))
        only22 = T("only 22 comparisons", 28, YOU_COL).to_corner(DR, buff=0.6)
        self.play(FadeIn(only22, shift=UP * 0.2), run_time=0.5)

        # B5: every pair ------------------------------------------------------------------
        self.wait_until(cue("comparing", 2))
        pairs = [(i, j) for i in range(23) for j in range(i + 1, 23)]
        chords = VGroup(*[Line(dots[i].get_center(), dots[j].get_center(), stroke_width=1,
                               color=CHORD_COL).set_stroke(opacity=0.55) for i, j in pairs])
        n_pairs = ValueTracker(0)
        counter = always_redraw(lambda: T(f"{int(n_pairs.get_value())} pairs", 40, CHORD_COL)
                                .to_corner(DR, buff=0.6))
        self.play(FadeOut(only22), FadeOut(you_lbl), yours.animate.set_color(CHORD_COL).set_stroke(width=1, opacity=0.55),
                  you.animate.set_color(PEOPLE_COL), answer.animate.set_opacity(0), run_time=0.5)
        self.remove(yours)
        self.add(counter)
        draw_until = cue("pairs", 1) + 0.2   # "...two hundred fifty three pairs"
        rt = draw_until - self.renderer.time
        self.play(LaggedStart(*[Create(c) for c in chords], lag_ratio=0.02),
                  n_pairs.animate.set_value(253), run_time=rt, rate_func=linear)
        self.bring_to_front(dots)

        # B6: each pair is a small chance -------------------------------------------------
        self.wait_until(cue("each"))
        chance = T("each pair: a 1-in-365 chance", 28, GREY_A).to_corner(UL, buff=0.6).shift(DOWN * 0.9)
        self.play(FadeIn(chance, shift=RIGHT * 0.2), run_time=0.6)
        self.wait_until(cue("match"))
        ring_hi = Circle(radius=0.32, color=MATCH_COL, stroke_width=4).move_to(
            (dots[9].get_center() + dots[22].get_center()) / 2)
        match_lbl = T("match!", 28, MATCH_COL).next_to(ring_hi, RIGHT, buff=0.1).shift(UP * 0.2)
        self.play(Create(ring_hi), FadeIn(match_lbl), Flash(ring_hi, color=MATCH_COL), run_time=0.7)

        # B7: multiply the misses -> curve crosses 1/2 at 23 --------------------------------
        self.wait_until(cue("multiply"))
        web = VGroup(year, chords, dots, ring_hi, match_lbl)
        self.play(FadeOut(chance), FadeOut(counter), web.animate.scale(0.55).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3),
                  title.animate.scale(0.8).to_edge(UP, buff=0.35), run_time=0.9)
        formula = T("P(no match)  ≈  (364/365)²⁵³  ≈  0.50", 30, WHITE)
        formula.next_to(title, DOWN, buff=0.35).shift(RIGHT * 1.9)
        self.play(Write(formula), run_time=1.2)

        ax = numbered_axes([0, 70, 10], [0, 1, 0.5], x_length=7.2, y_length=3.6)
        ax.to_edge(RIGHT, buff=0.6).shift(DOWN * 0.6)
        ylab = T("chance two people match", 22, GREY_A).next_to(ax.y_axis, UP, buff=0.15).align_to(ax, LEFT)
        xlab = T("people in the room", 22, GREY_A).next_to(ax.x_axis, DOWN, buff=0.45)
        half_line = DashedLine(ax.c2p(0, 0.5), ax.c2p(70, 0.5), color=GREY_B, stroke_width=1.5)
        self.play(Create(ax), FadeIn(ylab), FadeIn(xlab), Create(half_line), run_time=0.8)

        n = ValueTracker(1)
        curve = always_redraw(lambda: ax.plot(p_match, x_range=[1, max(n.get_value(), 1.01), 0.25],
                                              color=CURVE_COL, stroke_width=4))
        head = always_redraw(lambda: Dot(ax.c2p(n.get_value(), p_match(n.get_value())),
                                         color=PEOPLE_COL, radius=0.08))
        self.add(curve, head)
        self.wait_until(cue("drops") - 0.3)
        self.play(n.animate.set_value(23), run_time=cue("half") - self.renderer.time + 0.15,
                  rate_func=smooth)
        at23 = T("23 people → 50.7%", 26, PEOPLE_COL).next_to(ax.c2p(23, p_match(23)), RIGHT, buff=0.25).shift(DOWN * 0.3)
        self.play(FadeIn(at23, shift=UP * 0.15), run_time=0.4)

        # B8: by 70 it's nearly certain ------------------------------------------------------
        self.wait_until(cue("by"))
        self.play(n.animate.set_value(70), run_time=cue("ninety") - self.renderer.time - 0.1,
                  rate_func=smooth)
        big = T("99.9%", 72, PEOPLE_COL).next_to(ax.c2p(70, 1), DOWN + LEFT, buff=0.35)
        at70 = T("at 70 people", 24, GREY_A).next_to(big, DOWN, buff=0.1)
        self.play(FadeIn(big, scale=1.3), FadeIn(at70), run_time=0.5)
        self.wait_until(cue("percent"))
        self.play(Indicate(big, color=WHITE, scale_factor=1.12), run_time=0.9)
        self.wait_until(WORDS[-1]["end"] + 1.4)   # hold the payoff frame
