# Toolchain: what you need to match this quality

## Core (required)

| Tool | Why | Install (macOS) |
|---|---|---|
| **Python 3.10+** | Manim is a Python library | `brew install python` or `uv` |
| **Manim Community (ManimCE)** | The animation engine. Documented, stable, big plugin ecosystem. **Default choice for this repo.** | `uv venv --python 3.12 && uv pip install manim` |
| **Cairo + Pango + pkg-config** | ManimCE's renderer and text layout | `brew install cairo pango pkg-config` |
| **LaTeX (with dvisvgm)** | `MathTex`/`Tex` and axis numbers render through LaTeX. Without it you get the plain-text fallback in `explainer/style.py`, which is fine for drafts but not for finals. | `brew install --cask mactex-no-gui` (≈5 GB, full) or `brew install --cask basictex` then `sudo tlmgr install standalone preview doublestroke relsize fundus-calligra wasysym physics dvisvgm rsfs wasy cm-super everysel babel-english` |
| **FFmpeg** | Encodes Manim's output and does your final muxing | `brew install ffmpeg` |

> **ManimCE vs ManimGL (3b1b/manim).** Grant Sanderson's own version is
> [3b1b/manim](https://github.com/3b1b/manim) ("ManimGL"). It renders with OpenGL, has a fast
> interactive workflow (`manimgl file.py Scene -se <line>` drops you into an IPython shell
> mid-scene), and handles 3D/shaders better. It is also, in his own words in the video
> description, scrappy and not well documented, and its API is **not** compatible with ManimCE.
> Start with [ManimCE](https://github.com/ManimCommunity/manim). Switch to ManimGL only if you
> need its live-preview loop or heavy 3D. To read real production code, browse
> [3b1b/videos](https://github.com/3b1b/videos), where every 3b1b video's scenes are public
> (ManimGL syntax).

## Strongly recommended

| Tool | Why |
|---|---|
| **[manim-voiceover](https://github.com/ManimCommunity/manim-voiceover)** | Syncs animations to narration: `with self.voiceover(text=...) as tracker: self.play(..., run_time=tracker.duration)`. Works with a recorded voice or with TTS for drafts. This is the biggest time saver for timing. |
| **[manim-slides](https://github.com/jeertmans/manim-slides)** | Turns scenes into a click-through deck for storyboarding or live talks |
| **VS Code + the Manim Sideview extension** | Re-renders a scene preview on save |
| **Inkscape / Figma** | Draw custom SVG paths (characters, icons, curves to feed `epicycles.py`) |

## Audio (half of perceived quality)

* **Microphone:** a dynamic USB/XLR mic (e.g. Shure MV7+ or SM7B with an interface). Dynamics
  reject room echo, which matters more than the mic's price.
* **Recording/editing:** Audacity (free), Reaper (cheap), or Adobe Audition.
* **Clean-up:** iZotope RX or Adobe Podcast Enhance for noise and de-essing; target about −16 LUFS
  for YouTube.
* **Music:** 3b1b uses an original score (Vincent Rubinetti), which you can't reuse. Commission a
  composer or use a licensed library (Epidemic Sound, Artlist, Musicbed). Keep it quiet and
  piano-led, about −30 dB under the voice.

## Editing and delivery

* **NLE:** DaVinci Resolve (free) or Premiere/Final Cut. You only *assemble* here: Manim clips
  plus voice plus music plus chapter markers. All the animation happens in code.
* **Render settings:** `manim -qk` (4K60) or `-qh` (1080p60) for finals; `-ql` (480p15) while
  iterating.
* **Thumbnail:** the hero frame from your scene (`manim -s` saves the last frame as a PNG), plus
  3–5 words max.
* **Captions:** export your script as an SRT. Manual captions beat auto ones and help search.

## Things you should **not** copy

* The **pi creatures**, the 3b1b logo, and the music are 3Blue1Brown's identity. Design your own
  mascot or "voice of the viewer" device if you want that effect.
* Both Manim versions are MIT-licensed, so the *library* is free to use.

## Verified in this repo

On macOS (Nov 2026) with Python 3.12 + Manim Community v0.22.1 (installed by ./setup.sh), the example scenes render with
no LaTeX installed, thanks to the fallback in `explainer/style.py`. Install LaTeX to get real
Computer Modern maths.
