"""Starter scene. Every beat is pinned to a narration word with play_at / play_until.

Before voice.mp3 exists, timings are estimated from script.txt, so you can draft first:
    explainer render <slug>          # fast 480p draft
    explainer build <slug> --hq      # voice + music + 1080p60 + mix
"""
from explainer import *


class Main(VoiceScene):
    def construct(self):
        # Beat 1: hook / question
        title = title_card("1 + 3 + 5 + 7 + … = ?")
        self.play_at("here", Write(title), run_time=1.5)

        # Beat 2: build the picture, one odd number at a time, as each is spoken
        side = 0.55
        squares = VGroup()
        colours = [SUBJECT, SECONDARY, HILITE, STRUCTURE]
        for k, word in enumerate(["one", "three", "five", "watch"]):
            # the k-th odd number is an L-shaped layer of 2k+1 unit squares
            layer = VGroup(*[Square(side, stroke_width=2, color=colours[k], fill_opacity=0.35)
                             .move_to(np.array([x, -y, 0]) * side)
                             for x in range(k + 1) for y in range(k + 1) if x == k or y == k])
            squares.add(layer)
            self.play_at(word, FadeIn(layer, lag_ratio=0.2), run_time=0.8)
        self.play(squares.animate.move_to(DOWN * 0.3), run_time=0.6)

        # Beat 3: payoff
        result = T("= n²", 72, SUBJECT).next_to(squares, RIGHT, buff=0.8)
        self.play_at("squares", Write(result))
        self.hold_end()
