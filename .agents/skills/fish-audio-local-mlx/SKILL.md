---
name: fish-audio-local-mlx
description: Local Apple Silicon MLX Fish Audio S2-Pro 8-bit text-to-speech with anchor-clone voice consistency and English emotion instruction prompts.
---

# Local MLX Fish Audio S2-Pro — Anchor Unification & Emotion Steering

This skill defines the voice production contract for **Fish Audio S2-Pro (MLX Local 8-bit)** on Apple Silicon.

## HARD RULES (Binding)

1. **Emotion Prompts MUST be in English**: The `instruct` parameter MUST always be written in **English** (e.g., `"fast-paced, high-energy esports commentator shouting with excitement"`, `"tense and urgent, breathless delivery"`). The spoken `text` is Korean.
2. **Anchor-Sample Unification via Clone Mode**:
   - Generate the first/climax section as the **Anchor Sample** (`fish_anchor.wav`).
   - Clone every subsequent narration segment from the anchor using:
     ```python
     fish_tts.execute({
         "text": "<Korean text>",
         "reference_audio": "<path_to_anchor.wav>",
         "reference_text": "<exact transcript of anchor>",
         "instruct": "<English emotion instruction>", # ← ALWAYS ENGLISH
         "speed": 1.15,
         "temperature": 0.7,
         "output_path": "<output_wav_path>"
     })
     ```
3. **100% Local & Free**: Runs via `/Users/paul/fish-clean-venv/bin/python` with `mlx_audio` Metal GPU acceleration. Zero API keys, zero cloud costs.

## Quality Rubric

| # | Check | Requirement |
|---|-------|-------------|
| 1 | Anchor generated first | Anchor WAV path and exact reference text recorded in asset manifest |
| 2 | English instruction prompt | `instruct` is strictly in English; never Korean |
| 3 | Single unified voice | All subsequent segments pass `reference_audio=anchor.wav` |
| 4 | Speed & pacing | Fast-paced hype commentary uses `speed: 1.15 ~ 1.2` |
