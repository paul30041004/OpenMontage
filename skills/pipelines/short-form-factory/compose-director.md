# Compose Director — Short-Form Factory

## When to Use
Render the final 1080x1920 (9:16) MP4 video via HyperFrames Atelier or Remotion.

## Runtime Routing (read first)

Route by `edit_decisions.render_runtime`, locked at the idea stage and recorded as the `render_runtime_selection` decision:

- `hyperframes` → render through `video_compose`'s HyperFrames route (`hyperframes_compose`); confirm the runtime first with `operation="doctor"`.
- `remotion` → render through `video_compose`.

Never rewrite `render_runtime` in `edit_decisions` to make a render work. If it disagrees with the approved decision, stop: surface it to the user, send the choice back to the idea stage, append a corrected `render_runtime_selection` entry, then resume.

## Quality Standards
1. **Resolution:** 1080x1920 @ 30fps/60fps H.264 / AAC.
2. **Safe-Zone Check:** Verify subtitles and overlays do not collide with platform UI.
3. **Verification:** ffprobe stream and duration verification.
4. **Output:** Schema-valid `render_report` and `final_review`.
