---
name: voicestudio
description: Use when synthesizing speech or cloning voices via the local VoiceStudio (OmniVoice-Studio) speech platform running on localhost:3900. Supports 16 open-source TTS engines and 646 languages through an OpenAI-compatible audio API.
---

# VoiceStudio (OmniVoice-Studio) Integration Guide

VoiceStudio is a local, private speech platform that exposes an OpenAI-compatible audio endpoint (`http://localhost:3900/v1`). It runs on macOS Apple Silicon (MPS/MLX), Linux, and Windows, packaging 16 TTS engines and 646 languages without external cloud dependencies.

## 1. When to Use
- When synthesizing speech in non-English/non-Korean languages across the 646-language catalogue.
- When performing zero-shot voice cloning using locally installed models (OmniVoice, CosyVoice 3, VoxCPM2, IndexTTS).
- When a user prefers a fully local, offline ElevenLabs alternative running on `localhost:3900`.
- When accessing multiple model families through one unified OpenAI-compatible endpoint.

## 2. API Endpoint & Schema
- Base URL: `http://localhost:3900/v1`
- Method: `POST /v1/audio/speech`
- Request Payload:
  ```json
  {
    "model": "tts-1",
    "input": "안녕하세요, VoiceStudio 로컬 보이스입니다.",
    "voice": "default",
    "response_format": "wav",
    "speed": 1.0
  }
  ```

## 3. Supported Engines in VoiceStudio
- **OmniVoice** (default): 600+ languages, zero-shot cloning, voice design.
- **CosyVoice 3**: High-fidelity cloning, emotion instruction.
- **VoxCPM2**: Expressive acting and Korean voice cloning.
- **IndexTTS 2.5**: High accuracy Chinese, English, Japanese synthesis.
- **PocketTTS / Supertonic 3**: Ultra-lightweight CPU fallback.

## 4. OpenMontage Integration
The adapter tool `voicestudio_tts` connects directly to this server:
```python
from tools.audio.voicestudio_tts import VoiceStudioTTS

tool = VoiceStudioTTS()
result = tool.execute({
    "text": "안녕하세요, 반갑습니다.",
    "model": "tts-1",
    "voice": "default",
    "output_path": "output/voice.wav"
})
```
