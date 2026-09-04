# Compose Director — Short-Form Factory

## When to Use
Render the final 1080x1920 (9:16) MP4 video via HyperFrames Atelier or Remotion.

## Quality Standards
1. **Resolution:** 1080x1920 @ 30fps/60fps H.264 / AAC.
2. **Safe-Zone Check:** Verify subtitles and overlays do not collide with platform UI.
3. **Verification:** ffprobe stream and duration verification.
4. **Output:** Schema-valid `render_report` and `final_review`.
