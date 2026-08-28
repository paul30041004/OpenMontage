---
name: audio8-tts
description: Audio8 TTS 0.1B local autoregressive speech synthesis and zero-shot voice cloning. Use for lightweight (~170M parameter) local TTS across Korean, English, Chinese, and Japanese with reference audio cloning.
---

# Audio8 TTS 0.1B — Compact Zero-Shot TTS

Audio8 TTS Preview 0.1B is a high-efficiency autoregressive speech generation model featuring:
- **Compact Footprint:** ~170M parameter main model + 120M neural audio codec decoder (~0.4GB memory footprint).
- **Zero-Shot Voice Cloning:** Clone any voice using `reference_audio` + `reference_text`.
- **Multilingual Support:** Chinese, English, Korean, Japanese, German, Spanish, French, Italian.
- **Local & Free:** Runs locally on Apple Silicon (MPS), CUDA, or CPU with zero API costs.

## Calling Convention

```python
from tools.tool_registry import registry
registry.discover()
audio8 = registry.get("audio8_tts")

# 1. Zero-Shot Voice Cloning
result = audio8.execute({
    "text": "안녕하세요! 오늘은 에덴동산 서버 폭망 썰을 풀어보겠습니다.",
    "reference_audio": "assets/audio/my_reference.wav",
    "reference_text": "참고 음성 텍스트 내용",
    "temperature": 0.7,
    "top_p": 0.9,
    "output_path": "projects/my-project/assets/audio/scene-1.wav"
})

# 2. Direct Speech Generation
result = audio8.execute({
    "text": "안녕하세요! 숏폼 음성 합성 테스트입니다.",
    "output_path": "projects/my-project/assets/audio/output.wav"
})
```

## Best Practices
1. **Reference Quality:** Use 3–10 seconds of clean, noise-free reference audio with matching `reference_text` for maximum cloning similarity.
2. **Device Optimization:** Automatically utilizes `mps` on Apple Silicon Macs and `cuda` on NVIDIA GPUs.
3. **Punctuation:** Use natural Korean commas and ellipses (`...`) for realistic breath pauses and human prosody.
