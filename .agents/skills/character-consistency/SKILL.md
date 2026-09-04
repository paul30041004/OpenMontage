# Character Consistency (Cloud Video-Gen)

Keep ONE character looking the same across many AI-generated scenes. This is the
OpenMontage adaptation of ViMax's character-anchoring pattern, wired into the
existing video-generation fleet (seedance, veo, higgsfield, minimax, etc.).

## When to use

- A video with a recurring character (narrator, protagonist, mascot) that must
  keep the SAME face/build/outfit across multiple generated scenes.
- Any pipeline that calls `video_selector` / `veo_video` / `seedance_video` /
  `higgsfield_video` with `reference_image_paths`.

Do NOT use for the local rigged `character-animation` pipeline (SVG/Canvas rigs) —
that already has its own `character_design`/`rig_plan`/`pose_library` system.

## The pattern (binding workflow)

1. **Define the character once** — write a concrete, identity-anchoring
   `appearance` string (age, face, build, clothing, hair, distinguishing marks).
   The SAME string must appear in every reference prompt so the image model
   reproduces the same character.

2. **Generate anchor reference frames** — `character_consistency_builder`
   (operation=`generate_frames`) renders one or more identity portraits per
   character via the image-selector layer and fills `reference_frames` and
   `binding_hints.reference_image_paths`.

3. **Bind into video generation** — for every scene that features the character,
   pass the character's `reference_image_paths` to the video tool:
   ```python
   video_selector.execute({
       "prompt": "<scene action prompt>",
       "reference_image_paths": character["binding_hints"]["reference_image_paths"],
       "operation": "image_to_video",   # or reference_to_video where supported
       "aspect_ratio": "16:9",
       "output_path": "scene_n.mp4",
   })
   ```
   Prefer providers with strong character consistency: `higgsfield_video`
   (`character_consistency: True`), `seedance_video`, `veo_video`,
   `minimax_video`, `runway_video`.

4. **Reuse first_frame for scene openings** — `binding_hints.first_frame_path`
   (the canonical anchor) can be passed as `first_frame_path` to
   `veo_video`/`minimax_video` for `first_last_frame_to_video` continuity.

## Tool

- **Tool**: `character_consistency_builder`
- **File**: `tools/character/character_consistency.py`
- **Capability**: `character_animation`
- **Artifact**: `character_consistency` (`schemas/artifacts/character_consistency.schema.json`)

### Operations

| operation | What it does |
|-----------|--------------|
| `build` | Normalize character specs into a schema-valid `character_consistency` artifact (no image gen). |
| `generate_frames` | Also render anchor reference frames per character via `image_selector`, fill `reference_frames` + `binding_hints.reference_image_paths`. |

### Inputs

| Field | Purpose |
|-------|---------|
| `characters[]` | `id`, `role`, `appearance`, optional `reference_prompt` (composed from appearance + style if omitted) |
| `style.visual_style` | Shared visual language applied to every reference prompt |
| `views` | Anchor views to render per character (default `["front"]`) |
| `aspect_ratio` | Reference frame aspect (16:9, 9:16, 1:1) |
| `output_dir` | Where reference frames are written (use `projects/<p>/assets/characters/`) |
| `output_path` | Where to write the `character_consistency` JSON artifact |

## Identity-anchoring rules (critical for consistency)

- **One canonical appearance string per character.** Do not rephrase it across
  scenes — the model drifts. Embed it verbatim in `reference_prompt`.
- **Reuse the SAME seed/provider for a character's anchors** when regenerating.
- **QA every anchor frame before binding** — confirm the face/build/outfit match
  the intended identity across views. A bad anchor propagates to every scene.
- **Never mix anchors from different runs mid-video.** If the look must change,
  regenerate the anchor AND re-bind all scenes from the new anchor.
- **Anchored wording beats adjectives.** "tall, broad shoulders, square jaw,
  short gray-streaked hair, charcoal suit" outperforms "an imposing man".

## How scenes reference characters

Store per-character bindings in the `character_consistency` artifact. At the
`assets` stage of any cloud video pipeline, the agent maps each scene's featured
characters to their `binding_hints.reference_image_paths` and injects them into
the video generation call for that scene. The Backlot board can preview anchor
frames as a contact sheet before asset generation.

## Provenance

- Authored 2026-08-16 by bench-marking HKUDS/ViMax (agentic video generation)
  against OpenMontage. The ViMax strengths integrated here: per-character
  reference anchoring + cross-scene consistency + first-frame scene binding.
- Related: `tts-sample-unification` applies the same anchor→reuse discipline to
  narration voices.
