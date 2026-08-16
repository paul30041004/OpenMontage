---
name: dopamine-hype-motion-graphic
description: Forced-VoxCPM workflow template for dopamine-explosion style motion-graphic videos (5-min Korean hype explainers). Use when the user asks for a 자극적/흥미로운/도파민 폭발 style video, a hype kinetic-typography motion graphic, or any Korean narration-led motion graphic where expressive emotional TTS matters. MANDATORY: narration MUST use VoxCPM local TTS (voice design + emotion + clone mode) — Kokoro/Google TTS are prohibited. Full pipeline: research → proposal → script → scene_plan → assets → edit → compose (HyperFrames atelier) → publish.
---

# Dopamine Hype Motion Graphic — VoxCPM-Forced Workflow Template

This skill codifies the proven "dopamine-explosion motion graphic" workflow
(reference run: `projects/dopamine-molecule/`). It is a **template for any
short-to-medium Korean hype motion graphic** that must feel fast, urgent, and
viscerally engaging — countdowns, kinetic typography, neon-on-black, and
emotional narration.

## HARD RULES (binding)

1. **TTS = VoxCPM only.** `kokoro_tts`, `google_tts`, `openai_tts`, `piper_tts`,
   `doubao_tts`, `dashscope_tts` are PROHIBITED for this workflow's narration.
   Use `voxcpm_tts` (`tools/audio/voxcpm_tts.py`, provider `voxcpm`).
2. **Voice unification via clone mode.** Generate ONE anchor sample first
   (the most performance-sensitive section), get user approval, then clone all
   other segments from it using `reference_audio=<anchor.wav>` ONLY (do NOT pass
   `prompt_text` — VoxCPM 0.2+ CLI rejects it unless `prompt-audio` is also
   passed). See `.agents/skills/tts-sample-unification/SKILL.md`.
3. **Runtime = HyperFrames, composition_mode = atelier.** HTML/GSAP kinetic
   typography is the natural medium for exploding numerals and pulse motifs.
   Never silently swap to Remotion or FFmpeg.
4. **Everything local/free by default.** User preference in the reference run
   was "local free TTS" — VoxCPM is free (Apple MPS). Images may use
   `google_nano_banana` when Imagen is unavailable. Music via `google_music`
   (Lyria) with a two-track crossfade master if duration overruns.
5. **Pipeline is mandatory** — `animation` pipeline, stages in order:
   research → proposal → script → scene_plan → assets → edit → compose → publish.

## When to Use

- "5분짜리 자극적이고 흥미로운 영상 만들어줘" (5-min stimulating video)
- 도파민 폭발 / 도파민 분자 / 뇌과학 하이프 주제
- Korean narration-led kinetic-typography motion graphic
- Any brief that needs countdown reveals + emotional narration

## Prerequisites

| Layer | Resource |
|-------|----------|
| Pipeline | `pipeline_defs/animation.yaml` |
| Meta skills | `skills/meta/onboarding.md`, `skills/meta/reviewer.md`, `skills/meta/checkpoint-protocol.md`, `skills/meta/voice-performance-director.md`, `skills/meta/animation-runtime-selector.md`, `skills/meta/taste-direction.md`, `skills/meta/bespoke-composition.md` |
| Pipeline skills | `skills/pipelines/animation/*-director.md` (research, proposal, script, scene, asset, edit, compose, publish) |
| Layer 3 | `.agents/skills/tts-sample-unification/SKILL.md`, `.agents/skills/lyria/SKILL.md`, `.agents/skills/hyperframes*/`, `.agents/skills/voxcpm-tts/SKILL.md` |
| Tools (registry) | `voxcpm_tts`, `google_nano_banana` / `google_imagen`, `google_music`, `video_compose` (hyperframes), `audio_mixer`, `transcriber` |
| Artifacts | schemas in `schemas/artifacts/` (research_brief, proposal_packet, decision_log, script, scene_plan, asset_manifest, edit_decisions, render_report, final_review, publish_log) |

## Process

### Stage 0 — Preflight (mandatory)

Run preflight discovery and present the capability menu (see AGENT_GUIDE →
Mandatory Preflight). Confirm VoxCPM is AVAILABLE:

```bash
python -c "from tools.tool_registry import registry; registry.discover(); print(registry._tools['voxcpm_tts'].get_status())"
```

VoxCPM requires the model under
`~/.cache/huggingface/hub/models--openbmb--VoxCPM2/snapshots/__dl__`
(install via `tools/_bert_vits2/download_model.py`). If unavailable, the skill
BLOCKS narration — do not silently substitute another TTS; escalate to the user.

### Stage 1 — Research (`research-director.md`)

- Web-search the topic: landscape, trending, data points (≥3, target 5-8),
  audience insights/misconceptions, ≥2 animation-technique references.
- Angles: ≥3, each with `animation_fit`. For hype topics, favor
  `data_driven` / `contrarian` / `myth_busting` angles that pair with
  countdown visuals.
- Validate against `schemas/artifacts/research_brief.schema.json`.

### Stage 2 — Proposal (`proposal-director.md`)

- Present 3+ genuinely different concepts. For this template, all should be
  kinetic-typography-based with different narrative structures
  (e.g. countdown, myth-bust, comparison).
- **Present both runtimes** (Remotion + HyperFrames) with brief-specific
  pros/cons, recommend **HyperFrames atelier**. Record in decision_log
  (`render_runtime_selection`, both in `options_considered`).
- **Music plan is mandatory**: present Lyria generation vs Pixabay vs library.
- **Voice**: present VoxCPM as the locked choice (user preference: local free
  emotional TTS). Record `voice_selection` decision.
- Cost estimate: VoxCPM $0, images ~$0.04 each, Lyria ~$0.08/60s.
- Approval gate: `proposal_packet.approval.status` must be approved.

### Stage 3 — Script (`script-director.md` + `voice-performance-director.md`)

- Write in animation beats: one visual idea per section, countdown motifs.
- **Voice performance plan** is required at top level (`voice_performance`)
  with `pacing_profile: energetic`, `energy_curve`, `pause_policy`.
- Per-section `delivery_cues` with `provider_text` (punctuation-based pauses,
  NOT SSML — VoxCPM ignores SSML break tags).
- Set `sample_section_id` to the most performance-heavy section (the climax).
- Word/character count: Korean narration ≈ 4 chars/sec at normal pace; VoxCPM
  speaks faster (~3.5 chars/sec at default) — account for this in timing.

### Stage 4 — Scene Plan (`scene-director.md`)

- 5-aspect scene checklist per scene. For atelier kinetic scenes, camera and
  subject motion map to GSAP tween intent.
- Reuse strategy: countdown card layout system, pulse/spike motif, neon
  palette, transition family (cut/transform/slide/fade).
- Validate against `schemas/artifacts/scene_plan.schema.json`.

### Stage 5 — Assets (`asset-director.md`)

**Narration (MANDATORY VoxCPM):**
1. Generate the anchor sample from `sample_section_id`:
   ```python
   voxcpm_tts.execute({
     "text": <provider_text>,
     "voice_design": "(energetic young male narrator, deep and dramatic, hype style)",
     "emotion": "<Korean natural-language emotion, e.g. 긴장되고 무겁고 카리스마 있는 하이프 내레이터 톤>",
     "device": "mps",
     "output_path": "projects/<name>/assets/audio/voxcpm_<sec>_anchor.wav",
   })
   ```
   `voice_design` must be **English** (user rule d-011); `emotion`/`text` in
   **Korean**.
2. **Get user approval on the anchor sample** before batch (sample gate).
3. Batch clone every section from the anchor:
   ```python
   voxcpm_tts.execute({
     "text": <provider_text>,
     "reference_audio": <anchor.wav>,   # ← the approved anchor
     "device": "mps",
     "output_path": "projects/<name>/assets/audio/voxcpm_<sec>.wav",
   })
   ```
   Do NOT pass `prompt_text`. Record per-asset `voice_performance` in the
   asset_manifest (sample_path, provider_settings, clone contract).
4. **ffprobe every segment** — record real durations; feed back to scene_plan.

**Images:** `google_nano_banana` (gemini-3.1-flash-image) is the reliable
default (Imagen 4.0 may 404). 16:9 → ~1376×768; upscale or accept as dimmed
backgrounds. One image per scene, neon-on-black prompts, no readable text.

**Music:** `google_music` (Lyria 3 Pro). Hard limit 184s per generation. For a
5-min video, generate two tracks and build a crossfaded master with ffmpeg
(`acrossfade`, fade in/out, trim to exact duration). Probe the master.

### Stage 6 — Edit (`edit-director.md`)

- Rebuild scene timeline from ACTUAL VoxCPM narration durations (they differ
  from script estimates). Distribute leftover time as holds (countdown scenes
  get bigger holds).
- `edit_decisions`: render_runtime=`hyperframes`, renderer_family=
  `animation-first`, composition_mode=`atelier`.
- Narration segments mapped to scene starts; music with ducking.

### Stage 7 — Compose (`compose-director.md` → HyperFrames path)

1. `hyperframes_compose` operation=`scaffold_workspace` (copies assets).
2. Hand-author `projects/<name>/hyperframes/index.html` (atelier) — scenes as
   `section.clip` with `data-start`/`data-duration`/`data-track-index`, one
   paused GSAP timeline at `window.__timelines["<id>"]`, audio elements for
   narration + music, vignette/grain overlays.
   - **Determinism:** no `Math.random`, no `repeat:-1`; bounded repeats;
     finite tick arrays.
   - **Fonts:** Korean text needs NanumSquare TTF in `fonts/` (copy from
     `projects/viral-philosophy-shorts/hyperframes/fonts/`).
   - **CSS/GSAP conflict:** never pair CSS transform with a tween on the same
     property (use `gsap.fromTo`); add `overwrite:"auto"` for overlapping
     tweens.
3. Run `hyperframes lint` (0 errors) then `hyperframes validate`
   (contrast 0 failures) — both MUST pass before render.
4. `hyperframes render --output renders/final.mp4 --fps 30 --quality standard`.
5. Post-render self-review: ffprobe, sample 12 frames (no black frames),
   audio spotcheck across narration windows, Whisper transcription comparison.

### Stage 8 — Publish (`publish-director.md`)

- Package with YouTube metadata: title, description, chapters, hashtags.
- Thumbnail concept from a hero frame (e.g. the exploding numeral).
- Validate `publish_log`; present final to user.

## Self-Evaluation Rubric (score 0-1, pass ≥ 0.9)

| # | Check | Weight |
|---|-------|--------|
| 1 | VoxCPM used for ALL narration; anchor sample approved before batch; no Kokoro/Google TTS anywhere | 0.3 |
| 2 | All segments cloned from the anchor (`reference_audio` only), settings recorded per asset | 0.2 |
| 3 | Runtime locked to HyperFrames atelier; no silent swap; decision_log complete (pipeline, concept, runtime, composition_mode, music, voice) | 0.15 |
| 4 | lint 0 errors + validate contrast 0 failures before render | 0.15 |
| 5 | Post-render self-review: ffprobe OK, no black frames, narration audible, transcript matches script | 0.2 |

## Common Pitfalls

- **Silently falling back to Kokoro/Google TTS** when VoxCPM is slow or errors —
  this is a HARD RULE violation. Escalate, fix VoxCPM, keep VoxCPM.
- **Passing `prompt_text` to `voxcpm_tts`** — CLI rejects it
  (`--prompt-text requires --prompt-audio`). Use `reference_audio` only.
- **Korean `voice_design`** — must be English (d-011). Korean goes in
  `emotion`/`text`.
- **SSML break tags to VoxCPM** — ignored. Use punctuation/ellipsis for pauses.
- **Narration duration drift** — VoxCPM is faster than Kokoro; always ffprobe
  real segments and rebuild the scene timeline before compose.
- **`Math.random` / infinite `repeat:-1` in HyperFrames** — breaks deterministic
  seek-and-capture. Use fixed arrays and bounded repeats.
- **Missing NanumSquare fonts** — Korean renders as fallback glyphs; copy the
  TTFs into the HyperFrames `fonts/` dir.
- **5-min music** — Lyria caps at 184s; generate 2 tracks + ffmpeg acrossfade
  master (never loop-stretch without approval).
- **Imagen 4.0 404** — fall back to `google_nano_banana`; log the substitution
  in decision_log.
