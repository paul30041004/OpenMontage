# Compose Director — Novel-to-Video Pipeline

## When to Use

You are the **Compose Director** for an episode. You render the final video with
attention to grade, audio dynamics, and character-consistency preservation in the
output.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json` | Artifact validation |
| Prior artifacts | `edit_decisions`, `asset_manifest`, `scene_plan` (optional) | Timeline + media |

## Runtime Routing (MANDATORY first step)

Read `edit_decisions.render_runtime`:
- `remotion` — CinematicRenderer for reference-bound video clips + overlays.
- `hyperframes` — kinetic/HTML-driven treatment.
- `ffmpeg` — simple concat (rare for this pipeline).

`delivery_promise.motion_required=true` means the locked runtime is a commitment.
No silent swap. Pass `proposal_packet` to `video_compose.execute()` so the
runtime-swap check runs.

## Process

1. **Runtime preflight** — confirm the locked runtime is available before rendering.

2. **Render** — `video_compose` operation `render` with edit_decisions +
   asset_manifest + proposal_packet.

3. **Audio** — if narration/music were mixed separately, mux the approved mix.

4. **Character-consistency check (new for this pipeline)** — after render,
   sample frames across scenes featuring the same character and confirm identity
   holds (no face/outfit drift). Surface any drift in the render report warnings.

5. **Final review** — ffprobe validation, duration check, audio levels, runtime
   match. Render report + final_review.

## Quality Gate

- Output mood matches episode pacing; character consistency held across scenes;
  render_runtime matches proposal; output passes ffprobe.

---

## Gate Reminder

`human_approval_default: false` — proceed to publish once render validates.
