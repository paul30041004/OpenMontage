# Free Public Domain Documentary Production Workflow

> Comprehensive guide for producing high-production-value historical, scientific, space, and cultural documentaries utilizing **NASA, Wikimedia Commons, Internet Archive, Library of Congress, and NOAA** archives without any API keys, paid stock plans, or GPU requirements.

---

## 1. Overview & Public Domain Footage Ecosystem

OpenMontage's `direct_clip_search` connects directly to millions of hours of public domain and CC0/CC-BY archival media that are 100% free for commercial use and broadcast.

```
                  ┌─────────────────────────────────────────┐
                  │          Public Domain Archives         │
                  ├─────────────────────────────────────────┤
                  │ • NASA / ESA / JAXA (Space & Universe)  │
                  │ • Internet Archive (Historical / Retro) │
                  │ • Wikimedia Commons (Scientific / Nature│
                  │ • Library of Congress / NARA (History)  │
                  │ • NOAA (Oceans, Climate, Weather)       │
                  │ • Pexels / Pixabay (Modern Cinematic)   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                       [DirectClipSearch Fast Fetcher]
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
              [4K/HD Video Clips]            [Ultra-Res Still Images]
                        │                             │
                        ▼                             ▼
              [FFmpeg Fast Encode]           [Ken Burns Spring Zoom]
                        │                             │
                        └──────────────┬──────────────┘
                                       ▼
                       [Cinematic Documentary Master]
```

---

## 2. Archival Ingestion with `direct_clip_search`

Instead of relying on generic AI hallucinations or watermarked stock sites, pull authentic raw footage from the world's greatest archives:

```python
from tools.video.direct_clip_search import DirectClipSearch

dcs = DirectClipSearch()

# Space & Science Documentaries (NASA / ESA)
dcs.execute({
    "queries": [
        "Apollo 11 lunar surface moon landing",
        "James Webb space telescope deep field nebula",
        "Mars rover perseverance terrain"
    ],
    "sources": ["nasa", "esa", "wikimedia"],
    "clips_per_query": 2,
    "download_dir": "projects/<project_id>/assets/video"
})

# Historical & Geopolitical Documentaries (Archive.org / NARA / LOC)
dcs.execute({
    "queries": [
        "1960s Cold War mission control footage",
        "Industrial revolution factory machinery vintage",
        "World War II historical archives newsreel"
    ],
    "sources": ["archive_org", "nara", "loc"],
    "clips_per_query": 2,
    "download_dir": "projects/<project_id>/assets/video"
})
```

---

## 3. Cinematic Visual Post-Processing (CPU-Accelerated)

To give vintage archives or mixed-resolution footage a cohesive, high-end theatrical look:

### 1. Unified 1080p / 4K Fast Standardization
Always run non-standard archival aspect ratios through the standard 1920x1080 letterbox pad:
```bash
ffmpeg -i input_archive.mp4 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 19 output_clean.mp4
```

### 2. High-Res Stills Ken Burns Motion
For ultra-high-resolution museum and library photographs (LOC/Wikimedia):
* In Remotion: Use `interpolate(frame, [0, duration], [1.0, 1.15])` and slight pan `(x: -20px -> +20px)`.
* Avoid linear robotic zooms; use ease-in-out (`Easing.bezier(0.25, 0.1, 0.25, 1.0)`).

### 3. Geographic Journey Tracking (`GeoRouteMap`)
For historical expeditions or global trade routes, embed `GeoRouteMap` with animated path tracing and pulsing coordinate waypoints.

---

## 4. Voiceover & Sound Design Formula

* **Narrator Tone:**
  * **VoxCPM2:** Set `emotion="깊고 묵직한 목소리로 역사의 무게감을 전달하듯이"` with `voice_design="(distinguished, authoritative Korean documentary narrator, warm and deep)"`.
  * **EdgeTTS:** Use `en-US-ChristopherNeural` (English) or `ko-KR-InJoonNeural` (Korean) with `rate="-5%"` for gravitas.
* **Music Selection:**
  * Use `PixabayMusic` searching for `"cinematic ambient documentary orchestra strings"` or Classical Public Domain recordings (Musopen CC0).
  * Layer subtle room tone / wind / radio transmission sound effects from `Freesound` or built-in SFX assets.
