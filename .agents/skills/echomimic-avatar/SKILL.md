# EchoMimic — Audio-Driven Avatar Video (local)

Turns a portrait photo + an audio file into a **talking avatar video** on-device,
via `tools/avatar/echomimic_avatar.py` (provider `echomimic`, capability
`avatar`). No API key.

## What it does
- **Audio-driven**: one reference image (portrait/upper body) + any audio → MP4
  of the person speaking, with lip-sync and head motion.
- **Long-form**: chunked generation via the context window
  (`context_frames` / `context_overlap`) — audio longer than a single chunk is
  generated in overlapping segments with continuity, so 1-minute+ clips are
  possible (this is EchoMimic's `infer_audio2vid.py` context mechanism).

## Setup (one-time, big download)
```bash
python tools/_echomimic/setup_echomimic.py
```
Creates a dedicated venv (torch≤2.2.2, diffusers==0.24.0) and downloads the
audio-driven weights (denoising_unet ~3.4GB, reference_unet ~3.3GB,
motion_module ~1.8GB, face_locator, sd-vae-ft-mse, sd-image-variations-diffusers,
whisper). **GPU strongly recommended** — CPU inference is extremely slow.
If weights are missing the tool reports `status: unavailable/degraded`.

## Calling
```python
from tools.avatar.echomimic_avatar import EchoMimicAvatar
r = EchoMimicAvatar().execute({
    "reference_image": "projects/<id>/assets/images/portrait.png",
    "audio_path": "projects/<id>/assets/audio/mix.wav",
    "output_path": "projects/<id>/renders/avatar_clip.mp4",
    "device": "cuda",            # cuda preferred; mps/cpu fallback
    "width": 512, "height": 512, "fps": 24,
    "context_frames": 12,        # long-form chunk size
    "context_overlap": 3,
})
```

## Pipeline integration (avatar-spokesperson / hybrid)
- The `avatar-spokesperson` pipeline's assets stage can use `echomimic_avatar`
  as the avatar tool when the brief has a real portrait + narration audio.
- Typical flow: TTS/audio mix → `echomimic_avatar` → clip → `video_stitch` or
  `video_compose` (Remotion) to combine with scenes/titles.
- For long narrations, keep `context_frames` ≥ 12 and verify no drift at chunk
  boundaries in the post-render frame review.

## Layer 3 pointer
Engine + weights live at `tools/_echomimic/` (cloned antgroup/EchoMimic).
`infer_audio2vid.py` is the script the tool shells out to; `assets/` has sample
portraits and audios for a smoke test.

## Tips
- Square 512×512 crops of the face give the best lip-sync; keep the reference
  image well-lit and front-facing.
- The tool re-muxes the input audio onto the output MP4 if the pipeline's
  second pass doesn't emit an audio track.
- `fp16` is the default weight dtype; if output is glitchy on MPS, prefer `cuda`
  or drop to fp32 in `configs/prompts/animation.yaml`.
