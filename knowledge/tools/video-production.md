---
type: Tool
title: "Video Production Tools & Composition Rules"
description: "Remotion compositions (Explainer, EngineeringShortOverlay), VideoToolbox hardware acceleration, and ASS karaoke burners."
generated: { by: agent/cli, at: "2026-09-09T18:09:34Z" }
---

# Video Production Tools & Composition Rules

This document records the exact, verified tools and contracts for producing videos in OpenMontage.

## 1. Composition Engines

### Remotion (`remotion-composer/`)
React-based frame-accurate video renderer for Full HD (1920x1080) and 9:16 vertical shorts (720x1280 or 1080x1920).
- **Core Compositions**:
  - `Explainer`: Multi-scene presentations with spring physics, charts, cards, and animated audio waveforms.
  - `EngineeringShortOverlay`: High-tech 9:16 engineering shorts with measurement callouts, radar badges, and progressive scan lines.
  - `GenesisSeriesEpisode`: Automated 9:16 storytelling short with multi-frame image pan and caster narration.

### Critical Remotion Schema Invariants (HARD RULES)
1. **Audio Prop Schema**:
   MUST use nested structure: `audio: { narration: { src: "path.wav", volume: 1.0 } }`.
   *Never* pass flat `audio: { narrationSrc: "..." }` — doing so causes Remotion to skip the audio layer and produce a completely silent (-91 dB) video.
2. **StatCard Value**:
   The `stat` prop in `StatCard` must be a plain string (e.g. `stat: "~200ms"`), *never* an object `{ value, label }` (which triggers React Error #31).
3. **Audio Waveform Visualizer**:
   Use `type: "audio_waveform"` with `waveColor: "#00D4FF"` and `barCount: 40-50` for rendering dynamic glowing audio waveforms.

---

## 2. Hardware Acceleration & Post-Processing Tools

### VideoToolbox Encoder (`tools/video/videotoolbox_encoder.py`)
- Uses Apple Silicon M-series dedicated Media Engine hardware via FFmpeg (`h264_videotoolbox`, `hevc_videotoolbox`, `prores_videotoolbox`).
- Renders 10x faster than CPU encoding with near-zero CPU/RAM load (e.g. 15s 1080p video in 2.37s).

### ASS Viral Karaoke Burner (`tools/subtitle/ass_karaoke_burner.py`)
- Generates styled `.ass` subtitles with word-by-word active highlighting (Word-Pop in yellow/cyan), glowing dark outlines, and bottom-third safe margin padding.
- Hard-burns subtitles directly into MP4 using VideoToolbox in a single pass.

### Social Metadata Packager (`tools/publish/social_metadata_packager.py`)
- Extracts optimal high-contrast thumbnail frames (`thumbnail.jpg`) from the MP4.
- Generates high-CTR title, targeted hashtags, descriptions, and pinned comments into an upload-ready release bundle.

### OBS Studio Controller (`tools/video/obs_controller.py`)
- Controls OBS Studio via WebSocket (port 4455) for live scene switching, presentation streaming, and recording.

# Related Concepts
- [Voice Libraries & Audio Generation Stack](voice-libraries.md): integrates synthesized voices and masters audio into compositions
