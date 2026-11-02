# Compose Director — Video Composition Stage

Composes the final multimedia deliverable linking audio, score visuals, and synchronized lyrics.

## Runtime Routing (read first)

Route by `edit_decisions.render_runtime`, locked at proposal and recorded as the `render_runtime_selection` decision:

- `remotion` → render through `video_compose`.
- `hyperframes` → render through `video_compose`'s HyperFrames route (`hyperframes_compose`); confirm the runtime first with `operation="doctor"`.

Never rewrite `render_runtime` in `edit_decisions` to make a render work. If it disagrees with the approved decision, stop: surface it to the user, send the choice back to proposal, append a corrected `render_runtime_selection` entry, then resume. Map lyric timings from `subtitle_manifest` into the chosen runtime's composition and check a few reveals against the mastered audio.

## Quality Bar
- Synchronize lyric reveals with audio playback.
- Provide clean, legible typography with high-contrast presentation backgrounds.
- Render final video via Remotion or HyperFrames to produce standard 16:9 (1080p/4K) or 9:16 vertical shorts.
