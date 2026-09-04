---
name: breeze-tts
description: Breeze TTS 2 real-time bilingual (EN/ZH) text-to-speech with natural-language voice design, voice direction, zero-shot voice cloning, and vocal events (laugh, sigh, cough).
---

# Breeze TTS 2 — Real-Time Voice Design & Direction

Breeze TTS 2 (Breezeblue AI) is a top-ranked open-weight TTS model featuring:
- **Voice Design:** Reference-free natural language voice generation via `instruction`.
- **Voice Direction:** Clones voice from reference audio while steering tone, emotion, pace, and delivery via `instruction`.
- **Vocal Events:** Expressive inline cues: `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)`, `[笑]`, `[叹气]`.
- **Ultra-Low Latency:** Streaming inference with under 40ms TTFA on GPU.

## Calling Convention

```python
from tools.tool_registry import registry
registry.discover()
breeze = registry.get("breeze_tts")

# 1. Voice Design (Reference-free)
result = breeze.execute({
    "text": "(sigh) Welcome aboard. Your journey begins now.",
    "instruction": "A warm, thoughtful young woman with a clear voice and a calm, reflective delivery.",
    "cfg_scale": 4.0,
    "output_path": "projects/my-project/assets/audio/voice_design.wav"
})

# 2. Voice Direction (Reference Audio + Tone Steering)
result = breeze.execute({
    "text": "(clears throat) We need to discuss what happened last night.",
    "instruction": "Speak slowly with a restrained, serious tone.",
    "reference_audio": "reference.wav",
    "reference_text": "Exact transcript of reference audio",
    "cfg_scale": 4.0,
    "output_path": "projects/my-project/assets/audio/voice_direction.wav"
})
```

## Best Practices
1. **CFG Scale:** Use `cfg_scale: 4.0` to ensure strong adherence to natural-language instructions.
2. **Vocal Events Placement:** Insert events naturally between clauses (e.g. `"(laugh) That's unbelievable!"`).
3. **Reference Transcripts:** Always provide exact word-for-word `reference_text` when using `reference_audio` for optimal speaker similarity.
