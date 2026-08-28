---
name: qwen3-tts
description: Qwen3-TTS local text-to-speech on Apple Silicon MLX — premium Korean timbre (Sohee) for narration and natural-language voice design for character acting, across 10 languages.
---

# Qwen3-TTS — Narration & Character Acting (MLX)

Qwen3-TTS (Qwen team, Alibaba Cloud) is the current top-ranked open-weight TTS
family. Runs locally on Apple Silicon via `mlx-audio` with zero API cost.

## Role (binding)

Qwen3-TTS is used for **narration** and **character acting** — NOT voice cloning.

| Use case | mode | model |
|----------|------|-------|
| **Character acting** (연기·감정·페르소나) — **primary, user-approved 2026-08** | `voice_design` | `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` |
| Narration (fixed premium timbre) | `custom_voice` | `custom_0.6b` / `custom_1.7b` |

> **Voice cloning is NOT supported here.** The MLX port's Korean clone (Base
> model) is immature — 0.6B is low quality, 1.7B truncates output. For voice
> cloning use `chatterbox` (Multilingual v2, user-verified best) or `voxcpm_tts`.
>
> **Do NOT use `amps93/qwen3-tts-finetune-korean-*` repos** — tested 2026-08
> (instruct emotion matrix, male+female); user rejected the voice quality.
> Cache deleted (~4.2GB each); don't re-download.

## VoiceDesign 1.7B — Emotion Acting (user-approved 2026-08)

Verified emotion range on Korean text (same sentence, English instructs):
pitch swings 103→348 Hz across personas, speed 1.9x spread, full persona
switching (male anchor ↔ young woman) from one model.

```python
import mlx_audio.tts as tts
import soundfile as sf
import numpy as np

model = tts.load_model('mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16')
chunks = []
for chunk in model.generate(
    text="오늘의 주요 소식을 전해드리겠습니다.",
    instruct="Very excited Korean sports commentator voice, fast speaking rate, energetic and loud",
    lang_code="ko",
    verbose=False,
):
    chunks.append(np.array(chunk.audio if hasattr(chunk, 'audio') else chunk))
sf.write("out.wav", np.concatenate(chunks), 24000)
```

Verified persona instructs (English, Korean spoken text):
- `"Professional Korean male news anchor voice, clear, steady and trustworthy"`
- `"Very excited Korean sports commentator voice, fast speaking rate, energetic and loud"`
- `"Very sad elderly Korean male voice, low energy, slow and sorrowful"`
- `"Cheerful young Korean woman, bright high-pitched voice, playful and energetic"`

## Tool

`qwen3_tts` (`tools/audio/qwen3_tts.py`, provider `qwen3`, capability `tts`).

## Usage

```python
from tools.audio.qwen3_tts import Qwen3TTS
t = Qwen3TTS()

# 1. Narration — premium Korean female timbre
t.execute({
    "text": "안녕하세요, 반갑습니다.",
    "mode": "custom_voice",
    "model": "custom_0.6b",
    "voice": "sohee",          # Korean female
    "lang_code": "ko",
    "output_path": "assets/audio/sohee.wav",
})

# 2. Character acting — natural-language voice design
t.execute({
    "text": "오늘 하루도 평안하세요.",
    "mode": "voice_design",
    "model": "design_1.7b",
    "instruct": "warm, gentle middle-aged Korean woman, calm and comforting",
    "lang_code": "ko",
    "output_path": "assets/audio/design.wav",
})
```

## Speakers (custom_voice)

`serena`, `vivian`, `uncle_fu`, `ryan`, `aiden`, `ono_anna`, `sohee` (Korean),
`eric`, `dylan`.

## Character Acting Tips (voice_design)

- **`instruct` in English** (spoken text stays Korean) — English instructs
  react far stronger than Korean ones (verified on finetune A/B).
- Describe persona + emotion + delivery: e.g. `"cheerful young girl, high pitch,
  playful and energetic"`, `"gruff old man, low gravelly voice, slow and stern"`.
- For a consistent character across lines, reuse the same `instruct` and fix
  `temperature`/`seed` where possible.
- **Inline text tags (e.g. `(신나게) ...`) do NOT work** — they slow delivery
  instead. Always steer via `instruct`.
- Long single-shot narration degrades quality — segment by sentence and concat.

## Notes

- First load downloads the quantized model (~2-3 min); subsequent calls are fast.
- 10 languages: ko, en, ja, zh, de, fr, ru, pt, es, it.
