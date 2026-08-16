# Rhubarb Lip-Sync — phoneme-accurate 2D avatar (Mac CPU)

Drives a line-art narrator's mouth with **Rhubarb Lip Sync** timecodes for
exact per-phoneme timing — replacing Wav2Lip's neural output (which can drift)
where sync accuracy matters. Fits the book/ink series aesthetic.

## What it does
- Runs `rhubarb` on narration audio → mouth-shape cues (A-H, X) with precise
  start/end times (e.g. 43 cues for a 9s Korean narration).
- Renders 1280×720 line-art face frames per 24fps, switching mouth shape on
  the exact cue boundaries.
- Composites over any backdrop (`bg_path`) with the narration.

## Setup
- `tools/_rhubarb/rhubarb` (macOS x86_64 binary, v1.14.0) + `res/` (Sphinx
  model) — both copied from the GitHub release zip.
- Works under Rosetta on Apple Silicon.

## Calling
```python
from tools.avatar.rhubarb_lipsync import RhubarbLipsync
r = RhubarbLipsync().execute({
    "audio_path": "projects/<id>/audio/narration.wav",
    "output_path": "projects/<id>/renders/avatar.mp4",
    "bg_path": "projects/<id>/book_bg.mp4",   # optional backdrop
    "fps": 24,
})
```

## Why it syncs better than Wav2Lip
Rhubarb performs speech recognition and maps phonemes to mouth shapes with
frame-accurate timings; Wav2Lip generates mouth pixels from audio features but
its onset/offset can lag. For a 2D presenter the Rhubarb path is deterministic
and exact.

## Customization
- `render_face(shape)` in the tool draws the face + mouth — edit to restyle
  (colors, eyes, brows, mouth shapes).
- Swap the line-art style for a richer character by replacing `_mouth_draw`
  with shape SVGs if you have a rigged character.

## Pipeline
- Batch episodes: TTS (VoxCPM2 emotional) → `rhubarb_lipsync` (2D narrator)
  → book backdrop composite → titles/subtitles/BGM.
- Keep `wav2lip_avatar` for photoreal talking heads; use `rhubarb_lipsync`
  when timing precision matters most.
