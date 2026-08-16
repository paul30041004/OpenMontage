---
name: tts-sample-unification
description: |
  Unify all narration TTS segments to the FIRST anchor sample. Use when generating multi-segment voiceover/narration (a video script split into sections): generate one anchor sample first, then clone every subsequent segment from it so the whole narration shares one consistent voice. Triggers include "음성 샘플은 첫 샘플로 통일", "keep the voice consistent across segments", multi-section TTS batch generation, or any run where narration segments must not sound like different speakers.
---

# TTS Sample Unification — first sample is the anchor

Every multi-segment narration run in OpenMontage must use a **single unified voice**.
The rule: **generate the first sample first, then unify all later segments to it.**

Segments generated independently (even with identical settings) drift — local
stochastic models like VoxCPM vary slightly per call. That produces a narration
that sounds like several speakers. Fix: anchor on the first sample and **clone**
every other segment from it.

## Workflow (binding)

1. **Generate the anchor sample first.** Pick the most performance-sensitive
   section (per `skills/meta/voice-performance-director.md`, e.g. the climax
   quote) — or, per project convention, simply the first section. This WAV is
   the canonical voice reference for the entire run.
2. **Record the anchor contract.** Save to the asset manifest:
   - `sample_path` — the anchor WAV path
   - `prompt_text` — the exact text the anchor speaks (verbatim, same punctuation)
   - `provider_settings` — voice_design, emotion, device, and all other params
3. **Generate every later segment in clone mode** using the anchor:
   ```python
   tts.execute({
       "text": "<segment text>",
       "reference_audio": "<anchor.wav>",   # ← the first sample
       "prompt_text": "<anchor spoken text>",  # what the anchor says
       "voice_design": "<same as anchor>",
       "emotion": "<per-section emotion>",
       "device": "<same as anchor>",
       "output_path": "<segment path>",
   })
   ```
   Keep `voice_design`, `device`, and all voice-affecting settings identical to
   the anchor across every segment. Only `emotion`/`text` may vary per section.
4. **Never regenerate the anchor mid-run.** If voice direction must change,
   make a **new** anchor sample and re-clone **all** segments from it — never a
   mix of old and new anchors.
5. **Verify.** After the batch, spot-check that segments match the anchor
   (voice, pace, tone). Record the applied settings + sample approval on each
   narration asset in `asset_manifest[].voice_performance`.

## Provider notes

- **VoxCPM** (`tools/audio/voxcpm_tts.py`, provider `voxcpm`): clone mode via
  `reference_audio`. ⚠ CLI reality (voxcpm 0.2+, verified 2026-08): the CLI
  rejects `--prompt-text`/`--prompt-file` unless `--prompt-audio` is ALSO
  passed (`error: --prompt-text/--prompt-file requires --prompt-audio`).
  `--prompt-text` belongs to **continuation mode** (`--prompt-audio`), NOT to
  voice cloning. Therefore for voice unification, call `voxcpm_tts.execute`
  with `reference_audio=<anchor.wav>` and **DO NOT pass `prompt_text`** — the
  clone still yields a consistent voice. (If you want prompt-text fidelity,
  pass `prompt_text` AND `reference_audio` as `prompt-audio` — continuation
  semantics, use with care.)
- **Providers without clone mode** (e.g. cloud TTS): keep `voice_id`,
  `voice_design`, `speaking_rate`, `pitch` byte-identical across segments and
  document the settings on every asset — the anchor sample is still generated
  first and stored as the reference to compare against.
- **Sample-gate order matters:** the voice-performance sample approval step and
  the anchor step are the SAME step — the approved sample IS the anchor. Do not
  approve a sample and then batch with different voice settings.

## Related rules (project conventions)

- `voice_design` prompts must always be written in **English** (user rule, see
  decision_log d-011 in `viral-philosophy-shorts`).
- Pauses/emphasis come from `emotion` and punctuation; clone mode preserves the
  anchor's timbre but still follows per-section emotion cues.

## Self-Evaluation Rubric

Score each item 0–1 before checkpointing the assets stage; pass at ≥ 0.9.

| # | Check | Weight |
|---|-------|--------|
| 1 | A single anchor sample was generated FIRST and its WAV + spoken text + settings recorded | 0.3 |
| 2 | Every later segment was generated in clone mode (`reference_audio` = anchor, `prompt_text` = anchor text) or, for non-clone providers, with byte-identical voice settings | 0.3 |
| 3 | The anchor was never regenerated mid-run; a direction change produced a NEW anchor and ALL segments were re-cloned from it | 0.2 |
| 4 | `asset_manifest[].voice_performance` records sample_path, prompt_text, and provider settings for every narration asset | 0.1 |
| 5 | A post-batch spot-check confirmed segments match the anchor's voice | 0.1 |

## Common Pitfalls

- **Independent per-segment generation** — each call drifts (local models are
  stochastic), producing a multi-speaker narration. Always clone from the anchor.
- **Changing `voice_design` between segments** — the whole point of the anchor is
  one voice; only `emotion` and `text` may vary per section.
- **Regenerating the anchor to fix one segment** — this breaks unification.
  Fix the segment against the SAME anchor, or rebuild all segments from a new
  anchor; never mix.
- **Recording settings only on the sample** — every narration asset in the
  manifest must carry the applied clone/settings contract, not just the sample.
- **Clone without `prompt_text`** — fidelity can drop, but for VoxCPM 0.2+ the
  CLI **requires** `--prompt-audio` alongside `--prompt-text`, so passing
  `prompt_text` to `voxcpm_tts` will FAIL. Prefer `reference_audio` alone for
  cloning; the anchor voice is still unified. (See Provider notes.)
- **Korean text in `voice_design`** — `voice_design` must be English (d-011);
  Korean goes in `text`/`emotion` only.
