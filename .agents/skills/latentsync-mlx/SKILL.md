# LatentSync-MLX — Apple Silicon native lip-sync (local)

Highest-quality tier of the Mac avatar pipeline via
`tools/avatar/latentsync_avatar.py` (provider `latentsync`). Runs the
ByteDance LatentSync diffusion UNet/VAE natively on **Apple MLX** (≈2.3x faster
than PyTorch MPS) with Whisper + InsightFace preprocessing in PyTorch.

## What it does
- Audio-conditioned latent diffusion lip-sync: photo/face video + audio → the
  face speaks with strong lip-accuracy and face consistency (better than
  Wav2Lip's mouth-region paste).
- 256 (v1.5) / 512 (v1.6) resolution.
- Long-form via the standard chunk pipeline.

## Setup (done on this machine)
- `tools/_latentsync_mlx/` = sb1992/latentsync-mlx port
- `upstream/` = bytedance/LatentSync (preprocessing package)
- MLX weights (converted): `latentsync_unet_mlx.safetensors` (5.1GB),
  `vae_mlx.safetensors` (334MB); raw `latentsync_unet.pt` kept
- whisper `tiny` (auto-downloaded), InsightFace `buffalo_l` aux under
  `upstream/checkpoints/auxiliary/`
- Patches applied: decord→cv2/ffmpeg (`utils/util.py`), face_detector
  CUDA→CPU providers, whisper path→`tiny`, kornia/omegaconf installed.
- NOTE: `stable_syncnet.pt` removed to free disk (eval-only, not needed for
  inference).

## Calling
```python
from tools.avatar.latentsync_avatar import LatentSyncAvatar
r = LatentSyncAvatar().execute({
    "face": "projects/<id>/assets/images/portrait.png",  # or a face video
    "audio_path": "projects/<id>/assets/audio/mix.wav",
    "output_path": "projects/<id>/renders/avatar.mp4",
    "resolution": 256, "inference_steps": 20,
    "chunk_seconds": 120,
})
```
A photo input is auto-converted to a static video. Long audio is chunked and
concatenated.

## Performance (observed on this Mac, M-series CPU)
- ~60x realtime wall (10s clip ≈ 10 min, dominated by model load + MLX
  denoising + InsightFace CPU preprocessing). Plan long clips as background
  batch work; Wav2Lip (~1x realtime) is the fast tier, SadTalker (~50x) the
  middle tier.
- `inference_steps` 10 for drafts, 20 for quality.

## Pipeline integration
- `avatar-spokesperson` / `hybrid`: TTS → `latentsync_avatar` → clip →
  `video_stitch`/`video_compose`. Use LatentSync for hero shots, Wav2Lip for
  bulk/long content.

## Notes
- Needs the full ~6GB of MLX weights on disk; watch free space.
- v1.6 (512px) shows upstream mask artifacts at the boundary — prefer 256 for
  clean stills.
