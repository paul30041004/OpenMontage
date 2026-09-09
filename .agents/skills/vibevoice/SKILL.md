---
name: vibevoice
description: Microsoft VibeVoice frontier voice AI integration — ultra-low-latency real-time streaming TTS (0.5B, ~200ms latency, Korean supported) and 60-minute single-pass long-form ASR with joint diarization and custom hotwords.
---

# Microsoft VibeVoice Integration Guide

Microsoft VibeVoice (`microsoft/VibeVoice`) is an open-source frontier voice AI framework offering:
1. **VibeVoice-Realtime-0.5B**: ~200ms first-audio latency real-time streaming TTS (0.5B parameters, supports English, Korean, Japanese, French, German, Spanish, etc.).
2. **VibeVoice-ASR**: Unified 60-minute single-pass speech recognition producing structured `Who (Speaker), When (Timestamps), What (Content)` with customized hotword boosting and zero 30-second chunking boundaries.
3. **VibeVoice-ASR-BitNet**: Edge CPU inference engine compressed to 1.58GB with real-time inference (RTF < 1) on 3+ CPU threads via `VibeASR.cpp`.

## 1. When to Use
- **Real-Time Streaming Narration**: Use `vibevoice_tts` when immediate speech playback (~200ms) is needed for interactive agents, live previewing, or ultra-fast short-form narration.
- **Long-Form Audio Transcription & Podcast Repurposing**: Use `vibevoice_asr` when transcribing sermons, worship sessions, interviews, or podcasts up to 60 minutes in a single pass without losing speaker consistency.
- **Hotword Boosting**: Pass technical jargon, biblical names (`["카인", "아벨", "창세기"]`), or proper nouns in `hotwords: [...]` to guarantee zero misspelling.

## 2. Calling Convention

### VibeVoice Realtime TTS
```python
from tools.audio.vibevoice_tts import VibeVoiceTTS

tool = VibeVoiceTTS()
result = tool.execute({
    "text": "안녕하세요! 마이크로소프트 바이브보이스 실시간 스트리밍 음성입니다.",
    "speaker_name": "Carter",
    "language": "kr",
    "output_path": "output/narration.wav"
})
```

### VibeVoice Single-Pass ASR (Who + When + What)
```python
from tools.analysis.vibevoice_asr import VibeVoiceASR

tool = VibeVoiceASR()
result = tool.execute({
    "audio_path": "assets/sermon_60min.mp3",
    "hotwords": ["아벨", "카인", "에덴", "창세기"],
    "output_json": "output/transcript.json"
})
```

## 3. Presets and Local Assets
- **Korean Voice Presets**: Located in `tools/_vibevoice/voices/kr/`:
  - `kr-Spk2_woman.pt` (Female voice)
  - `kr-Spk3_man.pt` (Male voice)
- **Model Weights**: Auto-cached at `~/.cache/huggingface/hub/models--microsoft--VibeVoice-Realtime-0.5B` (0.5B, ~1.1GB).
- **Apple Silicon MPS Execution**: Runs natively using MPS acceleration and `sdpa` attention without CUDA.

## 4. Remotion Video Integration Contract
When composing Remotion videos (e.g. `Explainer`) with VibeVoice audio:
- **Audio Prop Schema (HARD RULE)**:
  Must use nested `audio: { narration: { src: "path.wav", volume: 1.0 } }`.
  NEVER use flat `audio: { narrationSrc: "..." }` (which leaves the render silent).
- **StatCard Cut Schema**:
  The `stat` field must be a plain string (e.g. `stat: "~200ms"`), NEVER an object `{ value, label }`.
- **Audio Waveform Cut Schema**:
  Use `type: "audio_waveform"` with `waveColor: "#00D4FF"` and `barCount: 40` to render the dynamic neural audio waveform.
