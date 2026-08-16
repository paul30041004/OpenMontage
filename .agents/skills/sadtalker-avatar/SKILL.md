# SadTalker Avatar — photo→talking head on Mac (local)

Turns one portrait photo + audio into a talking-head video (head motion +
lip-sync) via `tools/avatar/sadtalker_avatar.py` (provider `sadtalker`). Runs
on Mac CPU (`--cpu`); no CUDA needed.

## What it does
- **Photo → moving head**: head/pose motion + lip-sync driven by the audio
  (256px model for speed, 512px for quality).
- **Long-form**: chunk pipeline splits audio into `chunk_seconds` (default
  180s) pieces, renders each on the still photo, FFmpeg-concats.

## Setup (done on this machine)
- `tools/_sadtalker/` = cloned OpenTalker/SadTalker
- Models (from GitHub releases): `SadTalker_V0.0.2_256/512.safetensors`,
  `mapping_00109/00229-model.pth.tar`
- Face detection: `gfpgan/weights/alignment_WFLW_4HG.pth`,
  `detection_Resnet50_Final.pth`
- Dedicated venv (torch + basicsr 1.4.2 + facexlib + gfpgan). Two patches
  applied: `basicsr/data/degradations.py` → `functional.rgb_to_grayscale`
  (torchvision 0.28 compat), and setuptools pinned 69.5.1 (pkg_resources).

## Calling
```python
from tools.avatar.sadtalker_avatar import SadTalkerAvatar
r = SadTalkerAvatar().execute({
    "source_image": "projects/<id>/assets/images/portrait.png",
    "driven_audio": "projects/<id>/assets/audio/mix.wav",
    "output_path": "projects/<id>/renders/avatar.mp4",
    "size": 256,        # or 512 for higher quality (slower on CPU)
    "preprocess": "crop",
    "chunk_seconds": 180,
})
```
CPU throughput on this Mac ≈ 50x realtime (a 3.4s clip ≈ 3 min). Plan long
clips accordingly; the chunk pipeline keeps each render bounded.

## Pipeline integration
- `avatar-spokesperson` / `hybrid`: TTS audio → `sadtalker_avatar` (still
  portrait) → clip → `video_stitch`/`video_compose`.
- Works end-to-end local with `bert_vits2_tts` + `ebook_gen` + Remotion.

## Notes
- Faces that are small/heavily occluded degrade; use a clean front-facing
  portrait. `--preprocess full/extcrop` handles some framing cases.
- Enhancer (`gfpgan`) adds quality but needs the GFPGANv1.4.pth weight +
  much more CPU time — off by default.
- Official license: SadTalker is under MIT; weights come from the project's
  release assets.
