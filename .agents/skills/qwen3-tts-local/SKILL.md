---
name: qwen3-tts-local
description: Qwen3-TTS local voice cloning and CustomVoice TTS on Apple Silicon (official qwen-tts package, MPS). Use when cloning a voice from a reference audio file in a resource/asset folder (voice_library/, voice_samples/, assets/, test_audio/), or when using premium timbres incl. Korean 'Sohee'. Triggers include 보이스 클론, voice clone, 목소리 복제, 참조 음성으로 TTS.
---

# Qwen3-TTS Local — Voice Clone & CustomVoice (official qwen-tts, MPS)

Offline local TTS on Apple Silicon using the **official `qwen-tts` pip package**
(transformers-based) with locally downloaded weights — NOT the mlx-audio port.
This is the reliable path for Korean voice cloning.

## Models installed (local dirs)

| Model | Dir | Purpose |
|-------|-----|---------|
| **Base 1.7B** | `/Users/paul/qwen-tts-models/Qwen3-TTS-12Hz-1.7B-Base` | **voice cloning** — 3-second zero-shot clone from a reference clip |
| **CustomVoice 1.7B** | `/Users/paul/qwen-tts-models/Qwen3-TTS-12Hz-1.7B-CustomVoice` | 9 premium speakers, style instruction control |
| Tokenizer 12Hz | `/Users/paul/qwen-tts-models/Qwen3-TTS-Tokenizer-12Hz` | shared tokenizer (auto-loaded) |

Env: Python venv `/Users/paul/qwen-tts-venv` (`pip install -U qwen-tts`). MPS device. First load ~4-6s, generation ~1.8s/speech-second. 128GB RAM MacBook: both models can coexist, but load only the one you need per run.

## Tool

`qwen3_tts_local` (`tools/audio/qwen3_tts_local.py`, provider `qwen3_local`,
capability `tts`, runtime LOCAL_GPU, zero cost).

CLI helper: `python scripts/qwen3_tts_local.py …`

## Workflow

### 1. Discover reference audio (asset/resource folders)

```python
from tools.audio.qwen3_tts_local import Qwen3TTSLocal
r = Qwen3TTSLocal().execute({"mode": "discover_references"})
# -> {'count': 133, 'references': [{'path','name','duration_seconds'}, ...]}
```

Scanned roots (in order): `voice_library/`, `voice_samples/`, `assets/`,
`test_audio/` — recursive, `.wav/.mp3/.flac/.m4a/.ogg`.

CLI: `python scripts/qwen3_tts_local.py discover`

Guidance for picking a clip:

- **3–15s single speaker, clean, no music/noise** — best clone fidelity. voice_library clips are ~2-4s each (adequate; 5-15s is better).
- Longer clips (>30s, e.g. `voice_samples/` YouTube cuts) — trim to a clean 5-10s passage before cloning.
- Pass `reference_text` (the clip's transcript) whenever possible — it measurably improves similarity.

### 2. Clone the voice

```python
r = Qwen3TTSLocal().execute({
    "mode": "clone",
    "text": "새로 만드실 문장입니다.",
    "reference_audio": "comfort_heal.wav",   # bare filename auto-matched in the 4 roots
    "reference_text": "힘들면 잠시 쉬어도 괜찮아요. 오늘 하루도 수고했어요.",  # transcript of the ref clip
    "language": "Korean",                    # or Auto
    "output_path": "projects/<slug>/assets/audio/clone.wav",
})
```

CLI: `python scripts/qwen3_tts_local.py clone --ref comfort_heal.wav --ref-text "..." --text "..." --out out.wav`

### 3. Or use the premium Korean voice (CustomVoice, no reference needed)

```python
r = Qwen3TTSLocal().execute({
    "mode": "custom_voice",
    "text": "낭독하실 구절입니다.",
    "speaker": "Sohee",                      # warm Korean female, rich emotion
    "language": "Korean",
    "instruct": "잔잔하고 따뜻하게, 성경 구절을 낭독하는 느낌으로",  # optional style
    "output_path": "out.wav",
})
```

Speakers: `Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee`.
Use each speaker's native language for best quality, but any speaker can speak any of the 10 languages.

## Speaker reference (CustomVoice)

| Speaker | Description | Native |
|---------|-------------|--------|
| Vivian | Bright, slightly edgy young female | Chinese |
| Serena | Warm, gentle young female | Chinese |
| Uncle_Fu | Seasoned male, low mellow timbre | Chinese |
| Dylan | Youthful Beijing male | Chinese (Beijing dialect) |
| Eric | Lively Chengdu male, husky brightness | Chinese (Sichuan dialect) |
| Ryan | Dynamic male, strong rhythm | English |
| Aiden | Sunny American male, clear midrange | English |
| Ono_Anna | Playful Japanese female, light nimble | Japanese |
| Sohee | Warm Korean female, rich emotion | Korean |

## Tips

- **Clone fidelity**: shorter text → better consistency; keep each generation to 1-2 sentences. For multi-line narration, generate per sentence and concatenate (or pass a short list — the tool currently takes a single string; loop in your harness).
- **`reference_text` mismatch** degrades SIM score — transcribe the clip or use whisper if unknown.
- **Language hint**: set `language="Korean"` explicitly for Korean text (auto usually works, but explicit is safer).
- **instruct** on CustomVoice controls tone/emotion/prosody in natural language (Korean or English both work).
- **Consistency across lines**: clone once with `reference_audio`+`reference_text`, then reuse the SAME reference clip for every line. For batch runs, prefer building a `voice_clone_prompt` via `create_voice_clone_prompt` in the qwen-tts API.
- **Segmentation**: long single-shot generation degrades; split by sentence and concat via ffmpeg/sox.
- **Fallbacks**: `qwen3_tts` (mlx-audio port), `fish_audio_local_tts`, `voxcpm_tts` if this path ever fails.

## Verify outputs

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 out.wav
```

Expected: 24000 Hz mono WAV, duration ≈ text length × ~0.5s/Korean char.
