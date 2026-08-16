# Wav2Lip Avatar — Mac-friendly audio→talking-head (local)

Lip-syncs a face (still photo or short video) to any audio **on this Mac
(CPU/MPS, no CUDA)** via `tools/avatar/wav2lip_avatar.py` (provider `wav2lip`).

## What it does
- **Static photo → talking head**: one portrait + audio → MP4 of the portrait
  speaking with lip motion.
- **Short video → re-sync**: swap the mouth to match a new audio track.
- **Long-form (1h+ audio)**: a **chunk pipeline** splits audio into
  `chunk_seconds` (default 180s) pieces, lip-syncs each against the still face,
  then FFmpeg-concats — so arbitrarily long audio is handled without a single
  huge generation.

## Setup (weights already downloaded)
- `tools/_wav2lip/` = cloned Rudrabha/Wav2Lip
- `checkpoints/wav2lip_gan.pth` (436MB) — from the repo's Google Drive folder via `gdown`
- `face_detection/detection/sfd/s3fd.pth` (89MB) — direct URL
- Runs through `tools/_bert_vits2/venv/` (torch + librosa 0.9.2 + opencv-headless)

## Calling
```python
from tools.avatar.wav2lip_avatar import Wav2LipAvatar
r = Wav2LipAvatar().execute({
    "face": "projects/<id>/assets/images/portrait.png",  # or a short video
    "audio_path": "projects/<id>/assets/audio/mix.wav",   # any length
    "output_path": "projects/<id>/renders/avatar.mp4",
    "chunk_seconds": 180,   # long audio -> 3-min chunks -> concat
    "fps": 25,
})
```
For a 1-hour audio: the tool splits, lip-syncs each 3-min chunk on CPU
(≈ realtime or faster), and concatenates — no VRAM limits.

## Pipeline integration
- `avatar-spokesperson` / `hybrid` assets stage: TTS audio → `wav2lip_avatar`
  (still portrait) → clip → `video_stitch`/`video_compose`.
- Pairs with `bert_vits2_tts` (Mac TTS) for a fully-local presenter.

## Notes / limits
- Wav2Lip's open-source model quality is basic (commercial "lipsync-2" is
  higher quality); the mouth region is the main artifact — keep the face
  front-facing and well-lit.
- The official Wav2Lip license restricts commercial use (LRS2-trained).
- Chunk concat keeps the full audio; check boundaries for any lip drift.
- SadTalker (photo→moving head) and LatentSync-MLX/MuseTalk (Apple Silicon)
  are the next quality tiers in the roadmap.
