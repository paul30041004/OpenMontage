# Asset Director - Audiobook Pipeline

## When To Use

Third stage. Fixes the voices (anchors), then synthesizes and verifies every line.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifact | `script` (with `metadata.lines_path`) | Reviewed lines |
| Tools | `audiobook_builder`, `voxcpm_tts` | Anchor design and bulk synthesis |
| Layer 3 | `.agents/skills/voxcpm-tts`, `.agents/skills/tts-sample-unification` | Voice rules |

## Process

### 1. Voice Anchors (gate inside the stage)

Each speaker needs one anchor WAV in `projects/<id>/assets/audio/anchors/<speaker>_anchor.wav`.

- **Designed:** `audiobook_builder` `action: design_anchor` with an ENGLISH `voice_design` (rule d-011; no Korean, no parentheses) and a Korean `sample_text` of 2-3 natural sentences. Produce 2-3 candidates per speaker, letting the user pick.
- **Cloned:** user-supplied reference clip copied in as the anchor. Confirm they own the voice or have permission.
- **Reuse:** for a later chapter of the same book, copy the previous project's anchors unchanged. Never regenerate an anchor mid-book - the voice would drift.
- Do not add reverb or effects to an anchor unless the user asked.

Get the user to listen to each anchor and approve before step 2.

### 2. Bulk Synthesis

Call `audiobook_builder` `action: synthesize` with `lines_path`, `cast` (`{speaker: anchor_path}`) and `work_dir: projects/<id>/assets/audio/lines`. For each line it clones from the anchor, transcribes with Whisper, compares to `text`, retries up to `max_attempts` (default 5) until similarity reaches `accept_sim` (0.93) with a plausible duration, otherwise keeps the best attempt. It is resumable: re-running skips finished lines. The call blocks for a long time on a full chapter - run it in the background via a script wrapper only if the harness would otherwise time out, and report progress from `results.json`.

### 3. Review Weak Lines

`weak_lines` in the result are lines below the threshold. Open `results.json` and read `hyp` (what Whisper heard) for each:

- Digits/percent/number-word differences are Whisper normalisation, not a defect - accept.
- Real mispronunciations, dropped words or the emotion cue read aloud: delete that line's WAV and its `results.json` entry, adjust text/emotion in lines.json (merge short lines, spell out the problem word), run `synthesize` again.
- Headings like `제1장` that read wrong: write them phonetically (`제일장`).

### 4. Write The Asset Manifest

One `narration` asset per line (`id: line_0007`, `path`, `source_tool: audiobook_builder`, `scene_id` = the section label) and one `audio` asset per anchor (`source_tool: voxcpm_tts`, include the voice description in `prompt` where designed; omit the field instead of null). Put `lines_path`, `results_path`, weak-line decisions in `metadata`.

## Gate

Human approval required: anchors approved, weak lines resolved or accepted, line WAV count equals the line count.
