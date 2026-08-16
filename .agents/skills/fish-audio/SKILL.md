# Fish Audio TTS

Fish Audio is a cloud voice AI platform. This skill documents how OpenMontage uses
Fish Audio for high-quality cloud narration via the `fish_audio_tts` tool.

## When to use

- The user wants natural, non-robotic narration for a video (especially Korean or
  other languages where local TTS sounds artificial).
- Local TTS (VoxCPM, Kokoro, Bert-VITS2) produces robotic or mechanical output.

## Tool

- **Tool**: `fish_audio_tts`
- **Provider**: `fish_audio`
- **File**: `tools/audio/fish_audio_tts.py`
- **Capability**: `tts` (auto-included in `tts_selector`)

## Authentication

Set `FISH_API_KEY` in `OpenMontage/.env`:

```
FISH_API_KEY=sk-fish-...
```

Get a key at https://fish.audio/ (account → API keys / developers page).

**Important**: Fish Audio has TWO kinds of credit:
- **Platform credit** — for the web app.
- **API credit** — separate balance for API calls, managed at
  https://fish.audio/app/developers.

A `402 Insufficient API credit` error means the *API* balance is empty even if the
web-app balance is fine.

## Models

| Model | Cost | Notes |
|-------|------|-------|
| `s2.1-pro` | paid | Recommended production model. Lifelike, multilingual (incl. Korean). |
| `s2.1-pro-free` | **$0** | Same model quality, no TTFA/DPA guarantees, no credit required. Great for testing and small productions. |
| `s2-pro` | paid | Previous gen, multilingual + natural-language expression control. |
| `s1` | paid | Previous gen; uses `(parenthesis)` emotion tags. |

**Default in the tool**: `s2.1-pro`. If API credit is insufficient, use
`s2.1-pro-free` for zero-cost generation.

## Endpoint

`POST https://api.fish.audio/v1/tts`

- Headers: `Authorization: Bearer $FISH_API_KEY`, `Content-Type: application/json`,
  `model: <model>` (optional — omitted defaults to `s2.1-pro`).
- JSON body: `{ "text", "format", "reference_id"?, "prosody": {"speed"}?, "sample_rate"? }`
- Formats: `mp3` (default), `wav`, `pcm`, `opus`.

## Voice selection

- `voice` / `reference_id` — a Fish Audio voice model id from the Voice Library or
  a cloned voice. Omit to use the model default voice.
- For a consistent custom voice, clone once and pass the resulting `reference_id`.

## Mid-form / multi-segment voice cloning (unified narrator)

For any video with narration split across many sections (mid-form explainers,
documentaries, multi-scene pieces), keep ONE consistent voice across every segment
using a **persistent Fish Audio voice model**. This is the Fish Audio equivalent of
the `tts-sample-unification` pattern.

### Why

Local TTS is stochastic (drift), but even cloud TTS gives the most consistency when
every segment shares the same `reference_id`. Generate an anchor voice model once,
then every segment speaks in that exact voice.

### Workflow (binding for multi-segment narration)

1. **Generate the anchor sample first** — the most voice-sensitive line (per
   `skills/meta/voice-performance-director.md`, often the climax quote, or simply
   section 1). Save the WAV.
2. **Clone it into a persistent voice model**:
   ```python
   tts.execute({
       "operation": "create_voice",
       "reference_audio": "projects/<p>/assets/audio/anchor.wav",
       "reference_audio_text": "<exact anchor transcript>",   # sharpens pronunciation
       "voice_title": "narration-<project>",                   # optional
   })
   ```
   → returns a `reference_id` (a permanent Fish Audio voice model id).
3. **Record the anchor contract** in `asset_manifest`:
   - the anchor WAV path,
   - its exact spoken `reference_audio_text`,
   - the returned `reference_id`.
4. **Generate every later segment in clone mode** with the SAME `reference_id`:
   ```python
   tts.execute({
       "operation": "tts",
       "text": "<segment text>",
       "reference_id": "<anchor voice model id>",   # ← the cloned voice
       "model": "s2.1-pro-free",                     # or s2.1-pro if API credit funded
       "speed": 1.0,
       "output_path": "seg_<n>.wav",
   })
   ```
   Keep `model`, `speed`, `format`, `sample_rate` byte-identical across segments so
   only the spoken `text` varies.
5. **Never regenerate the anchor mid-run.** If the voice direction must change,
   make a NEW anchor + clone, then re-generate ALL segments from it — never mix two
   anchors' voices.
6. **Verify** after batch: spot-check segments match the anchor's voice, tone, and
   pace. Record `reference_id` + settings on every narration asset.

### Notes

- `operation="create_voice"` uses `POST /model` with `train_mode=fast` (usable almost
  immediately, `state` usually `trained`).
- Instant clone (inline reference audio per call) needs a MessagePack body; the
  JSON path does NOT support it. For one-voice-many-segments, ALWAYS use a persistent
  `create_voice` → `reference_id`.
- Free model `s2.1-pro-free` costs $0 but has no TTFA/DPA guarantees. For funded
  projects prefer `s2.1-pro`.

## Quality notes

- For non-robotic narration: prefer a cloud model (`s2.1-pro` / `s2.1-pro-free`) over
  local models when quality matters and an API key is available.
- Speed range: `0.5–2.0` via `prosody.speed`.
- Output WAV for highest fidelity when mixing (set `format=wav, sample_rate=44100`).

## Provenance

- Skill authored 2026-08-16 while integrating Fish Audio for
  `forbidden-bible-stories` after local VoxCPM narration was reported as robotic.
  Used `s2.1-pro-free` (paid `s2.1-pro` returned 402 due to empty API credit).
- Docs: https://docs.fish.audio/llms.txt
