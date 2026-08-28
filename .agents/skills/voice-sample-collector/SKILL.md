---
name: voice-sample-collector
description: Harvest natural human voice samples (15-20s MP3 clips) from YouTube/Shorts/Instagram/TikTok videos to improve TTS quality and build voice-clone reference corpora.
---

# Voice Sample Collector — Natural Human Voice Harvesting

Collect attractive, natural, real-human voice samples from SNS videos to power
higher-quality TTS (VoxCPM / Fish S2-Pro / Bert-VITS2 voice cloning).

## Tool

`voice_sample_collector` (`tools/audio/voice_sample_collector.py`, capability `training`).

## Workflow

1. **Download** best audio from a video URL via `yt-dlp` (YouTube, Shorts, Instagram, TikTok, 1000+ sites).
2. **Detect** continuous speech regions via FFmpeg `silencedetect` (inverse of silence).
3. **Cut** into 15-20 second MP3 clips (44.1kHz, 192kbps).
4. **Record** provenance in `voice_samples/manifest.json` (source URL, title, uploader, timestamps).

## Usage

```python
from tools.audio.voice_sample_collector import VoiceSampleCollector

collector = VoiceSampleCollector()
result = collector.execute({
    "url": "https://www.youtube.com/watch?v=...",
    "output_dir": "voice_samples",
    "segment_duration": 15.0,   # 15-20s recommended for TTS anchors
    "max_segments": 8,
    "language": "ko",           # optional metadata tag
})
```

## Best Practices

1. **Prefer single-speaker, clean speech** — talking-head vlogs, podcasts, ASMR, narration channels. Avoid music-heavy or multi-speaker debate content.
2. **15-20s is the sweet spot** — long enough to capture timbre/rhythm, short enough to be a clean anchor.
3. **Tag `language`** so the corpus stays searchable (ko/en/ja/zh).
4. **Curate after collection** — listen and delete clips with background music, laughter-only, or overlapping voices before using them as anchors.
5. **Feed curated clips as `reference_audio`** to `voxcpm_tts` / `fish_audio_local_tts` / `bert_vits2_tts` for voice cloning.

## Output Layout

```
voice_samples/
├── <video_id>_0001.mp3
├── <video_id>_0002.mp3
└── manifest.json          # provenance + timestamps
```
