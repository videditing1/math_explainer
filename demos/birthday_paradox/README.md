# Demo: the birthday paradox (30 s)

**Final video:** [birthday_paradox_final.mp4](birthday_paradox_final.mp4) (1080p60, 32 s, −16 LUFS) · thumbnail: [thumbnail.png](thumbnail.png)

Why this topic: it's widely known, the answer (23) feels wrong, and it has one
gorgeous visual reason, which is that 23 people make **253 pairs**.

| File | What |
|---|---|
| `script.txt` | narration (83 words ≈ 31 s) |
| `voice.mp3`, `voice.timing.json`, `voice.srt` | AI33 voice "George" (ElevenLabs Multilingual v2) + per-word timings |
| `birthday_paradox.py` | Manim scene; every beat is pinned to a narration word via `cue("word")` |
| `mix.sh` | voice normalised to −16 LUFS + music bed auto-ducked under the voice |
| `music.mp3` | *not committed* (licensed): Epidemic Sound "Starlit Fantasia" by Amber Glow |

## Rebuild
```bash
# from the repo root, with .env holding AI33_API_KEY and EPIDEMIC_SOUND_MCP_API_KEY
.venv/bin/python tools/ai33_tts.py demos/birthday_paradox/script.txt demos/birthday_paradox/voice
.venv/bin/python tools/epidemic.py call DownloadRecording \
  '{"id":"4536383a-5800-4517-8c7e-388e2ba3be02","options":{"fileType":"MP3","stemType":"FULL"}}'
#   → curl the returned assetUrl to demos/birthday_paradox/music.mp3
cd demos/birthday_paradox
../../.venv/bin/manim -qh --media_dir ../../media birthday_paradox.py BirthdayParadox
./mix.sh
```

## Beat sheet
| Time | Narration | Visual |
|---|---|---|
| 0.2 | "How many people…" | title + 365-day year ring draws |
| 4.5 | "Gut instinct… 180" | half the ring highlighted, grey "180?" |
| 8.0 | "The real answer… 23" | 180 crossed out, "23", 23 birthdays drop onto the ring |
| 10.2 | "…not comparing with yours" | "you" in pink, 22 lines from you |
| 13.7 | "…every pair… 253 pairs" | all 253 chords draw in, counter runs to 253 |
| 19.1 | "each one a small chance at a match" | the real shared birthday in this sample gets circled: "match!" |
| 21.4 | "Multiply the odds…" | web shrinks left, formula (364/365)²⁵³ ≈ 0.50, axes |
| 24.3 | "…drops below one half" | curve climbs to 23 → 50.7% |
| 26.1 | "By seventy… 99.9%" | curve runs to 70, "99.9%" lands on "ninety" |
