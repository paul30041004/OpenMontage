# Zero-GPU Viral Shorts Production Workflow

> Complete blueprint for producing high-retention, high-energy Shorts, Reels, and TikTok videos using **100% free, CPU-only open-source tools and zero-cost web assets**. No GPU or paid subscriptions required.

---

## 1. Core Architecture & Philosophy

This workflow eliminates all expensive cloud API costs and heavy GPU VRAM requirements by combining:
1. **Zero-Cost Neural Audio:** `edge_tts` (Microsoft Neural 70+ languages, 300+ voices) or `voxcpm_tts` (OpenBMB MPS/CPU local emotional acting).
2. **Audio-Driven Beat Synchronization:** `beat_sync_cutter` to mathematically align cuts, zooms, and text transitions with musical beats.
3. **High-Impact Motion Graphics:** Remotion React composition engine executing entirely on CPU (`npx remotion render`).
4. **Curated Free Visual Assets:** Pexels 4K/HD stock footage, Pixabay category clips, and dynamic procedural Canvas/SVG overlays.
5. **Pop-up Kinetic Subtitles:** Word-level highlighted subtitles styled with spring physics and auto-scaling.

```
[Script & Hook] ──> [EdgeTTS / VoxCPM Voiceover] ──> [Pixabay / Freesound BGM]
                            │                               │
                            ▼                               ▼
               [Word-Level Timestamp Sync]     [BeatSyncCutter (BPM/Onsets)]
                            │                               │
                            └───────────────┬───────────────┘
                                            ▼
                    [Remotion Frame-Accurate CPU Composition]
                     ├── 4K Free Stock Video Backgrounds
                     ├── Kinetic Subtitles (Word Highlight)
                     ├── Audio Waveform Visualizers
                     ├── Split-Screen / Device Mockups
                     └── Spring-Physics TextCards & StatCards
                                            ▼
                               [Final High-FPS MP4 Video]
```

---

## 2. Step-by-Step Production Sequence

### Phase 1: High-Retention Hook & Rapid Scripting (15s ~ 60s)
* **Pacing Rule:** Target **160–180 words per minute (WPM)** for Shorts.
* **0–3s Rule:** Never introduce yourself. Start directly with an impossible question, counterintuitive stat, or visual contradiction.
* **Information Density:** Switch visual angles or scene types every **1.5–2.5 seconds** (using `BeatSyncCutter` intervals).

### Phase 2: Zero-Cost Voiceover Synthesis
```python
from tools.audio.edge_tts_tool import EdgeTTS

tts = EdgeTTS()
result = tts.execute({
    "text": "당신이 방금 스크롤을 내린 건 당신의 의지가 아닙니다.",
    "voice": "ko-KR-InJoonNeural", # Or ko-KR-SunHiNeural / en-US-ChristopherNeural
    "rate": "+10%",                # Slightly brisk for Shorts retention
    "write_subtitles": True,       # Outputs word-aligned .srt
    "output_path": "projects/<project_id>/assets/audio/narration.mp3"
})
```

### Phase 3: Beat Analysis & Visual Cut Synchronization
```python
from tools.video.beat_sync_cutter import BeatSyncCutter

cutter = BeatSyncCutter()
beat_result = cutter.execute({
    "audio_path": "projects/<project_id>/assets/music/bgm.mp3",
    "cut_frequency": "every_4_beats",  # Fast kinetic cuts
    "target_duration_seconds": 60.0
})
cuts = beat_result.data["cuts"]
```

### Phase 4: Asset Acquisition (Free 4K / HD)
Use `pexels_video` or `direct_clip_search` for targeted B-roll:
```python
from tools.video.pexels_video import PexelsVideo

pv = PexelsVideo()
pv.execute({
    "query": "neon digital brain neural tech",
    "orientation": "portrait", # 9:16 for vertical Shorts
    "per_page": 3,
    "output_path": "projects/<project_id>/assets/video/clip_01.mp4"
})
```

### Phase 5: Composition & Motion Assembly (Remotion React)
Assemble using the `Explainer` or custom Atelier composition with vertical aspect ratio (1080x1920):
* Use `TextCard` with dynamic scale springs.
* Use `AudioWaveformVisualizer` for voiceover frequency reactions.
* Use `SocialQuoteCard` for citing authorities or tweet reactions.
* Use `DeviceMockup` for app, UI, or website showcases.

---

## 3. High-Conversion Visual Components Checklist

| Component Type | Remotion Component | Best Retention Use Case |
|---|---|---|
| **Big Numbers** | `StatCard` / `StatReveal` | Highlighting surprising stats (e.g., "99.9% 소멸") |
| **Tweet/Quote** | `SocialQuoteCard` | Quoting papers, news headlines, or viral tweets |
| **Side-by-Side** | `SplitScreen` | Before/After, Myth vs Reality, Good vs Bad |
| **Audio Spectrum** | `AudioWaveformVisualizer` | Podcast snippets, dramatic voiceover beats |
| **App Demo** | `DeviceMockup` | Showing mobile apps, articles, or screen recordings |
| **Terminal CLI** | `TerminalScene` | Tech tutorials, commands, code execution |

---

## 4. Subtitle & Audio Ducking Quality Standard
* **Ducking Rule:** Always reduce BGM volume by **-16dB to -18dB** during narration (`amix` filter or Remotion `volume` interpolate).
* **Subtitle Styling:**
  * Font: High-legibility sans-serif (`Pretendard`, `Black Han Sans`, `Montserrat`).
  * Colors: White text with vibrant yellow/cyan active word highlight (`#fde047` / `#38bdf8`).
  * Stroke/Outline: 2–4px dark outline (`#000000`) for universal legibility against all backgrounds.
