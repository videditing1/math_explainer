"""30-second demo: the birthday paradox.

Facts checked:  P(match | 23) = 0.5073,  P(match | 70) = 0.99916,  C(23, 2) = 253,
                (364/365)^253 = 0.4995 (the pairwise approximation shown on screen, marked ≈).

    explainer build birthday_paradox --hq
"""
import math

from explainer import *


def p_match(n: float) -> float:
    """P(at least one shared birthday among n people); smooth in n via log-gamma."""
    log_none = math.lgamma(366) - math.lgamma(366 - n) - n * math.log(365)
    return 1 - math.exp(log_none)


class Main(VoiceScene):
    def construct(self):
        # --- the year ring: 365 days around a circle -------------------------------
        R, centre = 2.45, DOWN * 0.35

        def day_point(d, r=R):
            a = PI / 2 - TAU * d / 365
            return centre + r * np.array([math.cos(a), math.sin(a), 0])

        months_at = np.linspace(0, 365, 12, endpoint=False)
        year = VGroup(
            Circle(radius=R, color=MUTED, stroke_width=2).move_to(centre),
            VGroup(*[Line(day_point(d, R - 0.08), day_point(d, R + 0.08), stroke_width=1.5,
                          color=MUTED) for d in months_at]),
            VGroup(*[T(m, 18, MUTED).move_to(day_point(d + 15, R + 0.35))
                     for m, d in zip("JFMAMJJASOND", months_at)]),
        )
        title = title_card("How many people until two share a birthday?")

        # 23 birthdays, with one genuine shared day (that's the point)
        rng = np.random.default_rng(7)
        days = list(rng.choice(365, 22, replace=False))
        days.append(days[9])  # person 23 shares a birthday with person 10
        dots = VGroup(*[Dot(day_point(d, R + (0.2 if i == 22 else 0)), radius=0.075, color=SUBJECT)
                        for i, d in enumerate(days)])

        # B1 question ---------------------------------------------------------------------
        self.play_at("how", Write(title, run_time=1.6), Create(year, run_time=2.4, lag_ratio=0.1))

        # B2 the gut guess ------------------------------------------------------------------
        half = Arc(radius=R, start_angle=PI / 2, angle=-PI, arc_center=centre,
                   color=GREY_C, stroke_width=8).set_stroke(opacity=0.5)
        guess = T("180?", 96, MUTED).move_to(centre)
        note = T("gut instinct: about half the year", 20, MUTED).next_to(guess, DOWN, buff=0.15)
        self.play_at("gut", Create(half), run_time=1.4)
        self.play_at("one", FadeIn(guess, scale=1.2), FadeIn(note, shift=UP * 0.2),
                     lead=0.1, run_time=0.7)

        # B3 the reveal -------------------------------------------------------------------------
        cross = crossed(guess)
        self.play_at("answer", Create(cross), run_time=0.5)
        answer = T("23", 110, SUBJECT).move_to(centre)
        self.play_at("twenty", FadeOut(VGroup(guess, note, cross, half)),
                     FadeIn(answer, scale=0.6), lead=0.15, run_time=0.5)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.12, run_time=1.0))

        # B4 not compared with *you* -----------------------------------------------------------
        you = dots[0]
        you_lbl = T("you", 24, HILITE).next_to(you, UP + RIGHT, buff=0.08)
        self.play_at("heres", answer.animate.scale(0.45).set_opacity(0.35),
                     you.animate.set_color(HILITE), FadeIn(you_lbl), run_time=0.6)
        yours = VGroup(*[Line(you.get_center(), d.get_center(), stroke_width=1.5, color=HILITE)
                         for d in dots[1:]])
        self.play_at("not", LaggedStart(*[Create(l) for l in yours], lag_ratio=0.05), run_time=1.3)
        only22 = T("only 22 comparisons", 28, HILITE).to_corner(DR, buff=0.6)
        self.play(FadeIn(only22, shift=UP * 0.2), run_time=0.5)

        # B5 every pair ---------------------------------------------------------------------------
        pairs = [(i, j) for i in range(23) for j in range(i + 1, 23)]
        chords = VGroup(*[Line(dots[i].get_center(), dots[j].get_center(), stroke_width=1,
                               color=STRUCTURE).set_stroke(opacity=0.55) for i, j in pairs])
        n_pairs = ValueTracker(0)
        count = counter(n_pairs, "{:.0f} pairs", 40, STRUCTURE, place=lambda m: m.to_corner(DR, buff=0.6))
        self.play_at("comparing", FadeOut(only22), FadeOut(you_lbl), FadeOut(yours),
                     you.animate.set_color(SUBJECT), answer.animate.set_opacity(0),
                     nth=2, run_time=0.5)
        self.add(count)
        self.play_until("pairs", LaggedStart(*[Create(c) for c in chords], lag_ratio=0.02),
                        n_pairs.animate.set_value(253), end=True, rate_func=linear)
        self.bring_to_front(dots)

        # B6 each pair is a small chance ---------------------------------------------------------
        chance = T("each pair: a 1-in-365 chance", 28, GREY_A).to_corner(UL, buff=0.6).shift(DOWN * 0.9)
        self.play_at("each", FadeIn(chance, shift=RIGHT * 0.2), run_time=0.6)
        hit = callout(VGroup(dots[9], dots[22]), "match!", DERIVED)
        hit[1].shift(UP * 0.2)
        self.play_at("match", Create(hit[0]), FadeIn(hit[1]), Flash(hit[0], color=DERIVED), run_time=0.7)

        # B7 multiply the misses -> curve crosses 1/2 at 23 ---------------------------------------
        web = VGroup(year, chords, dots, hit)
        self.play_at("multiply", FadeOut(chance), FadeOut(count),
                     web.animate.scale(0.55).to_edge(LEFT, buff=0.5).shift(DOWN * 0.3),
                     title.animate.scale(0.8).to_edge(UP, buff=0.35), run_time=0.9)
        formula = eq(r"P(\text{no match}) \approx \left(\tfrac{364}{365}\right)^{253} \approx 0.50",
                     "P(no match)  ≈  (364/365)²⁵³  ≈  0.50", 40)
        formula.next_to(title, DOWN, buff=0.35).shift(RIGHT * 1.9)
        self.play(Write(formula), run_time=1.2)

        ax = numbered_axes([0, 70, 10], [0, 1, 0.5], x_length=7.2, y_length=3.6)
        ax.to_edge(RIGHT, buff=0.6).shift(DOWN * 0.6)
        labels = axis_labels(ax, "people in the room", "chance two people match")
        half_line = DashedLine(ax.c2p(0, 0.5), ax.c2p(70, 0.5), color=MUTED, stroke_width=1.5)
        self.play(Create(ax), FadeIn(labels), Create(half_line), run_time=0.8)

        n = ValueTracker(1)
        self.add(always_redraw(lambda: ax.plot(p_match, x_range=[1, max(n.get_value(), 1.01), 0.25],
                                               color=SECONDARY, stroke_width=4)),
                 always_redraw(lambda: Dot(ax.c2p(n.get_value(), p_match(n.get_value())),
                                           color=SUBJECT, radius=0.08)))
        self.wait_until(self.cue("drops") - 0.3)
        self.play_until("half", n.animate.set_value(23), end=True, rate_func=smooth)
        at23 = T("23 people → 50.7%", 26, SUBJECT).next_to(ax.c2p(23, p_match(23)), RIGHT, buff=0.25).shift(DOWN * 0.3)
        self.play(FadeIn(at23, shift=UP * 0.15), run_time=0.4)

        # B8 by 70 it's nearly certain --------------------------------------------------------------
        self.wait_until(self.cue("by"))
        self.play_until("ninety", n.animate.set_value(70), rate_func=smooth)
        big = T("99.9%", 72, SUBJECT).next_to(ax.c2p(70, 1), DOWN + LEFT, buff=0.35)
        self.play(FadeIn(big, scale=1.3), FadeIn(T("at 70 people", 24, GREY_A).next_to(big, DOWN, buff=0.1)),
                  run_time=0.5)
        self.play_at("percent", Indicate(big, color=WHITE, scale_factor=1.12), run_time=0.9)
        self.hold_end()
