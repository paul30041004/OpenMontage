---
name: voxcpm-tts
description: VoxCPM2 local emotional TTS (OpenBMB) for OpenMontage. Use when generating Korean narration that needs emotional acting, voice design, or consistent voice cloning — the preferred narrator TTS for hype/dopamine-style videos. Requires the openbmb/VoxCPM2 model (~5GB) and Apple MPS/CPU. Use when the dopamine-hype-motion-graphic workflow mandates VoxCPM narration. MANDATORY for all Korean voice cloning — VoxCPM2 is the measured best Korean clone engine (SIM 0.919).
---

# VoxCPM2 — Local Emotional TTS

VoxCPM2 (OpenBMB) is the **mandatory** narration TTS for the
`dopamine-hype-motion-graphic` workflow. Fully local (Apple MPS / CPU), free.
Supports:

- **Voice Design** — natural-language voice + emotion description, no reference
  audio needed. "캐릭터 감정연기" tier.
- **Voice Cloning** — consistent speaker across a long video via
  `reference_audio` (clone mode).

## Korean Voice Cloning — MANDATORY (binding)

**All Korean voice cloning in OpenMontage MUST use VoxCPM2.** This is a
measured, binding decision (2026-09), not a preference.

Benchmark (same reference `voice_library/emotional.wav`, Resemblyzer SIM):

| Engine | Korean SIM | Verdict |
|--------|-----------|---------|
| **VoxCPM2** | **0.919** | ✅ use this |
| Fish Audio S2-Pro | 0.878 | ❌ not for cloning |
| Qwen3-TTS Base 1.7B | 0.841 | ❌ not for cloning |
| Chatterbox (Resemble AI) | 0.788 | ❌ not for cloning |

Language routing (do NOT cross-use):

| Language | Engine |
|----------|--------|
| **Korean** | **VoxCPM2** (this skill) |
| English | Chatterbox |
| Chinese / Japanese / multilingual | Qwen3-TTS |

Rules:

- A Korean clone request → route to `voxcpm_tts` clone mode. Never substitute
  Fish/Qwen3/Chatterbox for Korean cloning.
- **Parallel / fast-generation exception:** only when throughput matters (batch
  narration, many segments, tight deadline) may you use `fish_audio_local_tts`
  or `qwen3_tts_local` for Korean cloning as a speed fallback. VoxCPM2 remains
  the quality default; the fast engines are the throughput fallback, not the
  first choice. Log the substitution in `decision_log` (category
  `voice_selection`, subject "Narration TTS provider").
- If VoxCPM2 is unavailable, escalate (see Hard Rule 5) — do not silently fall
  back to another engine for a Korean clone.
- Reference audio for Korean cloning: pick from `voice_library/` (curated
  `voice_library.json` voices) or `voice_samples/`/`assets/`/`test_audio/`.

Tool: `tools/audio/voxcpm_tts.py`, provider `voxcpm`, runtime LOCAL.
Access via the registry (never import directly). VoxCPM2 model (~5GB) lives
under `~/.cache/huggingface/hub/models--openbmb--VoxCPM2/snapshots/__dl__`;
install via `tools/_bert_vits2/download_model.py`.

## Calling Convention

```python
from tools.tool_registry import registry
registry.discover()
voxcpm = registry._tools["voxcpm_tts"]

# 1) Anchor sample (voice design + emotion) — MUST be approved first
voxcpm.execute({
  "text": "<provider_text>",
  "voice_design": "(energetic young male narrator, deep and dramatic, hype style)",
  "emotion": "긴장되고 무겁고 카리스마 있는 하이프 내레이터 톤으로, 중요한 부분은 강조하며",
  "device": "mps",            # or "cpu"
  "output_path": "projects/<name>/assets/audio/voxcpm_<sec>_anchor.wav",
})

# 2) Batch — clone mode (reference_audio ONLY, never prompt_text)
voxcpm.execute({
  "text": "<provider_text>",
  "reference_audio": "projects/<name>/assets/audio/voxcpm_<sec>_anchor.wav",
  "device": "mps",
  "output_path": "projects/<name>/assets/audio/voxcpm_<sec>.wav",
})
```

## Hard Rules

1. **`voice_design` in ENGLISH** (user rule d-011). Korean goes in `emotion` /
   `text` only.
2. **Clone mode = `reference_audio` ONLY.** Do NOT pass `prompt_text` — the
   voxcpm 0.2+ CLI rejects `--prompt-text/--prompt-file` unless `--prompt-audio`
   is also passed. `prompt_text` belongs to continuation mode, not cloning.
3. **Pauses/emphasis from punctuation, not SSML.** VoxCPM ignores SSML break
   tags — use `...`, commas, and section breaks in `text`.
4. **Anchor never regenerated mid-run.** A voice-direction change requires a
   NEW anchor + re-clone ALL segments (see `tts-sample-unification`).
5. **Do not silently substitute another TTS.** If VoxCPM is unavailable or a
   segment fails, escalate — never fall back to Kokoro/Google/Piper for this
   workflow.
6. **Korean clone = VoxCPM2 only.** See "Korean Voice Cloning — MANDATORY"
   above. This overrides any other TTS routing for Korean cloning. Exception:
   parallel/fast batch generation may use Fish Audio or Qwen3-TTS (see the
   "parallel / fast-generation exception" in the MANDATORY section).

## Device Notes

- `mps` (Apple Silicon) is fast; `cpu` is slower but universal. Both local and
  free.
- First run downloads models if the cache is incomplete; expect ~5GB.
- Generation is stochastic per call — clone mode keeps the timbre unified but
  emotion/pacing still varies per section, which is desirable.

## Verification

- ffprobe each segment; record real durations (VoxCPM speaks faster than
  Kokoro — timeline must be rebuilt from measured durations).
- Listen to the anchor sample for voice, pace, pauses, emphasis before
  batch-generating the rest.
- Whisper-transcribe the final video to confirm narration content matches the
  script.
