# Production playbook: idea to upload

## 1. Pick the topic (1 day)
- [ ] A concept people *use* but don't *understand* (FFT, eigenvectors, backprop, entropy, e).
- [ ] Can it be titled **"But what is ___?"** or **"The ___ you were never shown"**?
- [ ] Is there a **hero visual** that is beautiful with the sound off? If not, keep looking.
- [ ] Find the **one central metaphor** (winding around a circle, arrows tip to tail). Every scene
      must live inside it.

## 2. Script (2–5 days, the most important step)
Write for the ear at ~180 wpm, so 15 min ≈ 2,700 words. Use the template from
`01-why-these-videos-work.md` §4. For every paragraph, write the **visual in a second column**:

| Narration | Visual | Scene/class |
|---|---|---|
| "Imagine wrapping this graph around a circle…" | line graph morphs into polar plot | `WindingMachine` beat 2 |

Checklist:
- [ ] Opens on the payoff visual plus a one-sentence promise.
- [ ] A concrete physical example comes before any symbol.
- [ ] Exactly one new idea per beat.
- [ ] At least one "now hang on, you might be thinking…" objection.
- [ ] At least one "pause and ponder".
- [ ] A summary every ~5 minutes.
- [ ] A real-world application roughly halfway through as a reward.
- [ ] The formula is assembled at the end, each symbol mapped to a piece of the metaphor, followed
      by the "now it means something" reframe.
- [ ] Simplifications are labelled honestly and caveats deferred to the description.
- [ ] The ending points to the bigger picture or the next video.

## 3. Storyboard (1 day)
Sketch keyframes, or render rough `-ql` scenes with placeholder text. Fix the **colour
assignments** now (`scenes/style.py`), because each concept keeps its colour for the whole video.

## 4. Build scenes (most of the time)
- One `Scene` class per script beat, roughly 20–90 s each. Short scenes re-render fast.
- Drive everything from `ValueTracker`s plus `always_redraw` so the views stay linked.
- Iterate at `-ql`, then render finals at `-qh`/`-qk`.
- See `04-manim-patterns.md` for which technique goes with which teaching move.

## 5. Voice
- Record in a treated room with the mic close. Do several takes per paragraph.
- Clean up (noise, breaths, de-ess), compress, and normalise to about −16 LUFS.
- Either sync with `manim-voiceover`, or cut the audio first and set each `run_time` to match.

## 6. Assemble
- NLE timeline: scene clips, voice, music bed, then 0.5–1 s of breathing room after each "aha".
- Chapter markers (`0:00 Title`, …) go in the description.
- Watch it once at 1.5× speed. Any moment where your eye doesn't know where to look needs a
  highlight (`Indicate`, `SurroundingRectangle`, dim the rest).

## 7. Package and publish
- [ ] Thumbnail = the hero frame + ≤5 words, readable on a phone.
- [ ] Title: curiosity + concept ("But what is the Laplace transform?").
- [ ] Description: chapters, links to deeper resources, credits to other creators, code link.
- [ ] Manual captions (SRT).
- [ ] A 30–60 s Short cut from the hero visual, linking to the full video.
- [ ] Publish the scene code (this repo). People remix it, which spreads the video.
