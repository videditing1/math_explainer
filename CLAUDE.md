# math_explainer: house rules

This repo produces 3Blue1Brown-*style* math explainer videos (original work, never copies of
3b1b's characters, music or branding). Read `docs/01-why-these-videos-work.md` before
writing any script.

## Pipeline (always use the CLI, never hand-roll ffmpeg/API calls)
```bash
source .venv/bin/activate          # or prefix commands with .venv/bin/
explainer doctor                   # tools, keys, credits
explainer new <slug>               # videos/<slug>/: script.txt, scene.py, video.toml, beats.md
explainer render <slug>            # 480p draft (timings estimated until voice exists)
explainer build <slug> --hq        # voice (AI33) → music (Epidemic) → 1080p60 → mix
```
Outputs: `videos/<slug>/<slug>_final.mp4` + `thumbnail.png`. Renders go to `media/<slug>/`.
`voice` and `music` skip if their files exist; pass `--force` to regenerate (costs credits).

## Writing a video
1. Fill in `beats.md` first: hook, gut guess, reveal, the one picture that explains it, formalise, payoff.
2. Write `script.txt` for the ear: ~180 wpm, so 30 s ≈ 80 words. Spell numbers as words
   ("twenty-three") so the TTS reads them naturally and `cue("twenty")` can find them.
3. Verify every number and claim in Python *before* animating; leave the check in a comment.
4. Scene = `class Main(VoiceScene)` in `scene.py`. Pin every beat to a word:
   `play_at("word", ...)` starts on it, `play_until("word", ...)` lands on it,
   `cue("two hundred")` accepts phrases, `hold_end()` holds the payoff frame.
5. Check the result: grab frames at each beat (`ffmpeg -ss T -i final.mp4 -frames:v 1 x.png`)
   and look at them. Check `ffmpeg -i final.mp4 -af ebur128 -f null -` ≈ −16 LUFS.

## Visual style (enforced by `explainer/style.py`)
- Black background, thin strokes, serif text (`T()`), maths via `eq(tex, plain_fallback)`.
- Semantic colours, fixed for the whole video: `SUBJECT` yellow (the thing studied),
  `SECONDARY` teal, `DERIVED` red (results/answers), `HILITE` pink ("you"/look here),
  `STRUCTURE` blue (connective lines), `MUTED` grey (guesses, labels).
- Nothing pops in: `Write`, `Create`, `FadeIn(shift=…)`, or transform from something on screen.
- ≤ 4 colours on screen; labels sit on objects; one new idea per beat.
- Live numbers via `counter(tracker, "{:.0f} pairs")` (no LaTeX needed).

## Secrets and licensing
- Keys live only in `.env` (gitignored). Never print, log or commit them.
- `music.mp3` is licensed Epidemic Sound audio: OK inside rendered videos, never committed
  (gitignored). `music.json` records which track was used.
- AI33 has no public docs; its API is documented in `explainer/ai33.py`.
