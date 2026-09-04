# Asset Director — Novel-to-Video Pipeline

## When to Use

You are the **Asset Director** for an episode. You generate the actual media:
per-scene reference-bound video clips (with characters anchored), narration
audio, music, and any support stills — each linked to scenes in the
`asset_manifest`.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifacts | `scene_plan`, `character_consistency`, `script` | Scenes + bindings + beats |

## Process

### 1. Sample Preview First (prevents wasted spend)

Generate ONE representative reference-bound scene (the lead character in one
beat) and show the user before batch generation. Confirm the anchor + motion
look consistent.

### 2. Reference-Bound Scene Videos

For each scene, generate its video clip via `video_selector`, binding every
featured character's reference images:

```python
refs = []
for cid in scene["featured_characters"]:
    refs += character_consistency[cid]["binding_hints"]["reference_image_paths"]

video_selector.execute({
    "prompt": "<scene action prompt>",
    "operation": "image_to_video",       # or reference_to_video where supported
    "reference_image_paths": refs,
    "preferred_provider": "<from binding_hints.preferred_providers>",
    "aspect_ratio": "<episode aspect>",
    "output_path": "projects/<p>/assets/video/scene_<id>.mp4",
})
```

- Prefer providers with strong character consistency (`higgsfield_video`,
  `seedance_video`, `veo_video`, `minimax_video`, `runway_video`).
- Use `first_frame_path` for scene openings where the provider supports
  first/last-frame binding.
- **Motion-required beats must be actual video clips**, never still substitutes.

### 3. Narration

Generate narration per script section via `tts_selector`. For a consistent voice
across the episode, follow `tts-sample-unification`: one anchor, reuse for all
segments (local clone or cloud reference_id).

### 4. Music

Resolve per the proposal's music plan (user library → royalty-free search → AI
generation). Instrumental underscore suited to the episode's emotional arc.

### 5. Manifest

Record every asset: scene-bound video, narration, music, support stills — with
provenance, provider, model, cost, and scene linkage. Every referenced file must
exist on disk.

## Quality Gate

- Every scene video binds its characters via reference_image_paths.
- Anchor frames and generated motion visually match (no identity drift).
- All referenced asset files exist.

---

## Gate Reminder (Binding)

Gates on human approval (`human_approval_default: true`). Checkpoint
`awaiting_human`, present the filmstrip (Backlot board renders the assets +
character anchors), and **END YOUR TURN**.
