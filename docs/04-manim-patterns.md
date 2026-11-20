# Manim patterns: teaching move to code

Each row maps something the 3b1b videos *do* to the ManimCE tool that does it.

| Teaching move (seen in the videos) | ManimCE tool | Example in this repo |
|---|---|---|
| One knob drives several linked diagrams (winding frequency → wound graph + centre of mass + transform plot) | `ValueTracker` + `always_redraw(lambda: ...)` | `winding_machine.py` |
| Live numeric readout ("2.00 cycles/second", `t = 0.36`) | `always_redraw` around `Text`/`DecimalNumber`, or `DecimalNumber.add_updater` | `freq_readout` |
| Sweep that slows near the interesting value ("chaos… whoop!") | a chain of `tracker.animate.set_value(x)` with different `run_time`s and `rate_func=linear` | the sweep loop |
| One representation *becomes* another (line graph → circle) | `ReplacementTransform(a.copy(), b)`, `TransformFromCopy` | first winding beat |
| Equation assembled piece by piece | `TransformMatchingTex`, `MathTex(..., substrings_to_isolate=[...])` | — |
| Colour = identity across symbols and pictures | `MathTex(tex, tex_to_color_map={"g(t)": YELLOW})`, matching the colour of the curve | `style.py` palette |
| Draw a path as it is traced | `TracedPath(lambda: point)` | `epicycles.py` |
| Rotating vectors tip to tail | complex arithmetic in NumPy + `Arrow`/`Circle` rebuilt by `always_redraw` | `epicycles.py` |
| "Look here" | `Indicate`, `Circumscribe`, `SurroundingRectangle`, `Flash`, or dim everything else with `.animate.set_opacity(0.2)` | final beat of `WindingMachine` |
| Zoom into the tiny fast arrows | `MovingCameraScene` + `self.camera.frame.animate.scale(0.1).move_to(p)` | — |
| Label a span ("the actual Fourier transform") | `Brace(mob, DOWN).get_text("...")` | — |
| Cross out the bit you drop (the `1/(t₂−t₁)`) | `Cross(mob)` | — |
| Graph + area (integral as average) | `Axes.plot`, `Axes.get_area`, `Axes.get_riemann_rectangles` | — |
| Complex plane | `ComplexPlane().add_coordinates()`, `n2p`/`p2n` | — |
| 3D surfaces (heat-equation sheets) | `ThreeDScene`, `Surface`, `self.move_camera(...)` | — |
| Load an arbitrary drawing to decompose | `SVGMobject(path)` + `point_from_proportion(t)` | `PATH_SVG=... epicycles.py` |

## Style rules baked into `scenes/style.py`
1. Pure black background, faint blue grid, thin strokes (2–3 px).
2. ≤4 colours on screen at once, and each colour means one thing all video.
3. Serif text for labels; LaTeX (Computer Modern) for maths.
4. Nothing pops in. Use `Create`, `Write`, `FadeIn(shift=...)`, or a transform from something
   already on screen.
5. Hold the frame for 1–2 s after every reveal (`self.wait`), so the narration lands.

## Commands

```bash
cd scenes
../.venv/bin/manim -pql winding_machine.py WindingMachine   # fast preview
../.venv/bin/manim -pqh winding_machine.py WindingMachine   # 1080p60 final
../.venv/bin/manim -s  -ql epicycles.py Epicycles           # save last frame (thumbnail)
PATH_SVG=logo.svg ../.venv/bin/manim -pql epicycles.py Epicycles
```
