# Dual-Engine Voice Production — VoxCPM & Local MLX Fish Audio S2-Pro

When the user requests dual-variant production or multi-voice comparison ("2개 영상 동시 생성", "A/B 렌더링", "VoxCPM과 Fish S2-Pro 둘 다로 만들어줘"), OpenMontage executes this workflow.

## Overview

One unified script and scene plan produces **two full video deliverables** in parallel:
- **Variant A (`renders/final_voxcpm.mp4`)**: Narration synthesized via `voxcpm_tts` (VoxCPM2 Local Apple Silicon MPS).
- **Variant B (`renders/final_fish_mlx.mp4`)**: Narration synthesized via `fish_audio_local_tts` (MLX Fish Audio S2-Pro 8-bit Local Metal GPU).

Both engines run **100% locally on Apple Silicon without cloud API fees**.

## Dual-Engine Voice Guidelines

| Engine | Voice Design / Emotion Prompt Rule | Anchor Cloning Method |
|---|---|---|
| **VoxCPM2** | `voice_design` in **English**, `emotion` in **Korean** | `reference_audio=anchor.wav` (do NOT pass `prompt_text` in VoxCPM 0.2+) |
| **Fish Audio S2-Pro (MLX 8-bit)** | `instruct` MUST BE IN **ENGLISH** | `reference_audio=anchor.wav` + `reference_text="<exact anchor transcript>"` |

## Workflow Stages

1. **Script & Scene Plan (Unified)**: Write standard animation beats and delivery cues.
2. **Dual Asset Batch Generation**:
   - **VoxCPM Batch**:
     - Generate anchor `assets/audio/voxcpm_anchor.wav`.
     - Clone sections: `voxcpm_sec_01.wav` ~ `voxcpm_sec_05.wav`.
   - **Fish S2-Pro Batch**:
     - Generate anchor `assets/audio/fish_anchor.wav`.
     - Clone sections with English `instruct`: `fish_sec_01.wav` ~ `fish_sec_05.wav`.
   - Measure real audio durations for both sets via `ffprobe`.
3. **Dual Composition Materialization**:
   - `hyperframes/index_voxcpm.html` aligned to VoxCPM timings.
   - `hyperframes/index_fish.html` aligned to Fish S2-Pro timings.
4. **Dual Render Execution**:
   - `hyperframes render ... --output renders/final_voxcpm.mp4`
   - `hyperframes render ... --output renders/final_fish_mlx.mp4`
5. **Presentation**: Present both variants to the user with a comparative breakdown of vocal timbre, pace, and dramatic energy.
