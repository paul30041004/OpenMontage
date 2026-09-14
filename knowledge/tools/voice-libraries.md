---
type: Asset
title: "Voice Libraries & Audio Generation Stack"
description: "Installed Synthesizer V Pro voices (SOLARIA II, ASTERIAN II), VibeVoice Realtime, VoxCPM2, and VoiceStudio 16-engine suite."
generated: { by: agent/cli, at: "2026-09-09T18:06:50Z" }
---

# Voice Libraries & Audio Generation Stack

This document records all available vocal models, local TTS engines, installed AI voice databases, and processing tools in OpenMontage.

---

## 1. Synthesizer V Studio Pro 2 (Installed AI Voices)

The user has a full professional installation of **Synthesizer V Studio 2 Pro** located at `/Applications/Synthesizer V Studio 2 Pro.app`.
Database files are located in `~/Library/Application Support/Dreamtonics/Synthesizer V Studio 2/databases/`.

### Verified Installed Voices by Role
- **Soprano (Lead Female)**: `SOLARIA II`, `SOLARIA`, `Natalie 2`, `Mai 2`, `Sheena 2`, `Aurielle`, `Kasane Teto AI 2`
- **Alto (Warm Female)**: `SAROS II`, `ANRI Arcane RDX`, `ANRI Requiem`, `Saki 2`, `Felicia 2`, `ROSE AI 2`
- **Tenor (Lead Male)**: `Kevin 2`, `Yuma 2`, `Ryo 2`, `Jin 2`, `JUN Nocturne`, `ANDI Vesper`, `Riku 2`
- **Bass / Baritone (Deep Male)**: `ASTERIAN II`, `Oscar 2`, `Hayden 2`, `Marvin`, `Danny`, `Archie`, `Ninezero 2`
- **Choral Groups**: `Choir Voices #1`, `Choir Voices #2`, `Choir Voices #3`

### Automation & Scripting
- `AutoExportActiveTracks.lua`: Located in `~/Library/Application Support/Dreamtonics/Synthesizer V Studio 2/scripts/` to confirm tracks and bounce stems with 1 click.
- `tools/audio/synthv_runner.py`: Injects 24-bit 48kHz render configuration directly into `.svp` projects and opens the editor.

---

## 2. Speech Synthesis & Cloning Engines

### Microsoft VibeVoice (`tools/audio/vibevoice_tts.py`)
- **Model**: `microsoft/VibeVoice-Realtime-0.5B` (0.5B parameters, ~200ms latency on Apple Silicon MPS).
- **Korean Presets**: `tools/_vibevoice/voices/kr/kr-Spk2_woman.pt` (Female) and `kr-Spk3_man.pt` (Male).
- **ASR**: `tools/analysis/vibevoice_asr.py` (60-minute single pass with custom hotword boosting).

### VoiceStudio Local Suite (`tools/audio/voicestudio_tts.py`)
- Connects to local VoiceStudio running on `http://localhost:3900`.
- Provides access to 16 TTS engines (OmniVoice, CosyVoice 3, VoxCPM2, IndexTTS) and 646 languages through an OpenAI-compatible audio API.

### VoxCPM2 Local Emotional TTS (`tools/audio/voxcpm_tts.py`)
- OpenBMB VoxCPM2 running in `projects/_shared/tts-venv/bin/voxcpm`.
- Measured best Korean voice cloning engine (SIM 0.919).
- Primary engine for high-energy eSports caster narrations, dramatic character acting, and biblical/sermon documentaries.
- **성경 및 설교 다큐멘터리 전용 보이스 프리셋**:
  - 앵커 음원: `voice_library/bible_sermon.wav` (중후하고 깊은 남성 다큐멘터리 톤)
  - 보이스 디자인: `dignified and deep male narrator, solemn and sorrowful biblical documentary tone`
  - 영문 Emotion Tag 원칙: 각 막의 감정선에 맞춘 영어 control prompt 적용 (e.g. `weary, mournful`, `intimate, reverent, tender wonder`, `deeply moving, tearful comfort`, `warm, gentle pastoral blessing`)
  - 오디오 파이프라인 원칙: 48kHz 무손실 스테레오 체인 유지, 48kHz 256kbps 이상 고해상도 BGM 믹싱 필수 적용.

### Qwen3-TTS Local (`tools/audio/qwen3_tts_local.py`)
- Official Qwen3-TTS running in `/Users/paul/qwen-tts-venv/` on MPS.
- Features premium Korean timbre 'Sohee' and 3-second zero-shot voice cloning.

---

## 3. Audio Post-Processing & Mastering Chain

- **Vocal Mastering (`tools/audio/vocal_mastering.py`)**: 80Hz rumble cut, 3.5kHz vocal clarity presence, 6.5kHz de-esser, Church/Hall reverb, accompaniment sidechain ducking (-2.5dB), and -14.0 LUFS EBU R128 loudness normalization.
- **Stem Separation (`tools/audio/stem_separator.py`)**: Meta Demucs v4 for isolating vocal tracks and extracting instrumental MR accompaniments.
- **Audio to MIDI (`tools/audio/audio_to_midi_transcriber.py`)**: pYIN monophonic pitch detection to standard `.mid` for sheet music/Synth V reverse-transcription.
- **Voice Anchor Cleaner (`tools/audio/voice_anchor_cleaner.py`)**: 24kHz mono normalization and VAD silence trimming for zero-shot cloning reference samples.
- **Korean Text Normalizer (`tools/audio/korean_normalizer.py`)**: Normalizes Bible citations (e.g. `창 4:1`), hymns (e.g. `통 115장`), dates (`유월`, `시월`), and native classifiers.
- **Emotion Router (`tools/audio/emotion_router.py`)**: Parses inline emotion markup (e.g. `[분노]`, `(긴박하게)`) and converts to model prompt parameters.
- **TTS Hallucination Guard (`tools/audio/tts_hallucination_guard.py`)**: Closed-loop ASR verification measuring Character Error Rate (CER) to prevent stuttering and repetition loops.
- **Batch Speech Processor (`tools/audio/batch_speech_processor.py`)**: Normalizes multi-scene voiceover segments to consistent -14 LUFS and triggers Apple Silicon MPS garbage collection.
