# Korean Voice Cloning — Standard Engine Workflow

**Effective**: 2026-09-05 (binding decision after engine benchmark on 손석희 reference).

## TL;DR

For **any Korean voice cloning** request in OpenMontage, route through **one of four engines** with these defaults. They were benchmarked on 손석희 8.28s clip with 3 sentences (baseline / sad / excited) — see `projects/son-bench/` for raw numbers.

| Engine | MFCC SIM | Avg RTF | Best For | Status |
|---|---|---|---|---|
| **voxcpm** | 0.998 | 9.22x | Quality-first, 48kHz, emotional | primary |
| **qwen3_local** | 0.998 | 6.26x | Stable clone, premium Korean timbre (Sohee) | primary |
| **omnivoice** | 0.998 | 3.79x | Speed + quality, 600 languages | primary |
| **ice012** | 0.997 | 1.86x | Speed-1st, lightest model (1.3GB), cc-by-nc-4.0 | primary |
| **higgs_v2_mlx** 🆕 | 0.99 | 0.5x | Mac MLX native, emotion control, **experimental** | experimental |

**Do NOT use** (for Korean cloning):
- `bert_vits2` — `soxr` module missing in this env
- `pocket-tts` — English only, no clone (gated anyway)
- `chatterbox` / `piper` / `kokoro` — registry unavailable
- `fish_audio_local` — lower SIM (0.994), only if multilingual needed
- `audio8` — removed (fixed length 11.89s, unnatural pacing)

## Engine Selection Matrix

### Use **voxcpm** when
- Hero work, single deliverable, emotional narration
- Need 48kHz output (mixing with high-res audio)
- Reference audio is **clean single-speaker, 5-15s**
- Willing to wait ~20s per clip

**Hard rules (binding)**:
1. Clone mode = `reference_audio` ONLY (no `prompt_text`)
2. Anchor sample never regenerated mid-run — every segment uses the same anchor
3. `voice_design` always in **English** even when text is Korean
4. Pause/emphasis from punctuation (`...`, `,`) — VoxCPM ignores SSML
5. If VoxCPM unavailable, **escalate, do NOT silently substitute**

### Use **qwen3_local** when
- Need premium Korean timbre (Sohee speaker) without a reference
- OR want zero-shot clone from 3-15s reference + reference_text
- 1-2 sentence per generation (long single-shot degrades)

**Hard rules**:
1. Always pass `reference_text` when cloning (transcribe via Whisper)
2. Pass `language="Korean"` explicitly (auto usually works, explicit is safer)
3. Build a `voice_clone_prompt` via `create_voice_clone_prompt` for batch consistency
4. For multi-line narration, generate per sentence and concatenate

### Use **omnivoice** when
- Speed matters AND quality must stay high (SIM 0.998)
- Multilingual project that may extend beyond Korean
- CPU-only path (mps may hang on some models per skill notes)

**Hard rules**:
1. Pass `ref_text` (transcript of reference_audio) — measurably improves similarity
2. `device="cpu"` is the stable default; `mps` may hang
3. `num_step=16` for speed, `32` for max quality

### Use **ice012** when
- Throughput matters most (3-5s per clip, 1.86x RTF avg)
- Many segments, tight deadline, or quick prototype
- Willing to accept cc-by-nc-4.0 license

**Hard rules**:
1. Always pass `ref_audio` AND `ref_text` for clone mode
2. Always pass `language="Korean"` (or detected language code)
3. `duration=None` (let model decide), `speed=1.0` default
4. Same `voice_state` model kept in memory between calls (already cached after first generation)

### Use **higgs_v2_mlx** (experimental) when
- Apple Silicon Mac **only** (MLX native, no GPU server needed)
- Short utterances (≤ ~6s) with emotion variation wanted
- Single-speaker clean reference available
- Workflow can tolerate slightly lower SIM (0.99 vs 0.998) for the convenience of inline emotion control

**Why experimental**:
- Output length is **unstable** — short sentences often hit `max_new_frames` cap rather than emitting EOS naturally. Always pass `max_new_frames` explicitly. Recommended: **200 for short, 300 for medium**.
- SIM 0.939-0.992 (vs 0.997-0.998 for the other four engines). Acceptable for short clips, watch for drift on long narration.
- 5.8GB q8 disk (bf16 is larger). First download takes ~5 min.
- Tested via `mlx-community/higgs-audio-v2-3B-mlx-q8`. The upstream `bosonai/higgs-tts-3-4b` is **GPU only** (SGLang-Omni) and **NOT usable on Mac**.

**Hard rules**:
1. Always pass `reference_audio_path` AND `reference_text` — ref text measurably improves clone fidelity.
2. Always set `max_new_frames` explicitly (default 900 → 36s, way too long). Use **200** for short clips, **300** for medium.
3. Reference audio MUST be 24kHz mono WAV — convert via `ffmpeg -i in.mp3 -ar 24000 -ac 1 -c:a pcm_s16le out.wav` first.
4. `temperature=0.7` default is fine. Higher = more expressive but less stable.
5. Do NOT mix with other engines mid-project — Higgs has distinct timbre characteristics.
6. Only the **v2** model is currently usable on Mac (MLX port exists). v3 + Boson Audio v2 + KRAFTON Raon-Speech are GPU-only.

## Reference Audio Standard (binding)

For best Korean clone results, the reference audio MUST meet these criteria:

| Spec | Minimum | Recommended |
|---|---|---|
| Length | 5s | 8-15s |
| Speakers | 1 | 1 |
| Background noise | quiet room | dead silent |
| Music | none | none |
| Content | clean speech | continuous monologue |
| Sample rate | any (auto-resampled) | 24kHz+ mono |
| Format | wav/mp3/flac | wav |

**Recommended reference clips** (already in repo):

| Speaker | Path | Length | Why |
|---|---|---|---|
| 손석희 (anchor) | `voice_samples_celebs/son_sukhee/tQzFIEEDh4U_0002.mp3` | 8.28s | Single-speaker news anchor, professional, clear |
| General library | `voice_library/*.wav` (133 clips) | 1-5s | Curation-purpose voices (emotional, comedy, narration, etc.) |

**Always transcribe first**:
```python
from tools.analysis.transcriber import Transcriber
t = Transcriber()
r = t.execute({"input_path": REF, "language": "ko", "model": "tiny"})
ref_text = " ".join(s["text"].strip() for s in r.data["segments"]).strip()
```

## Per-Engine Calling Conventions

### voxcpm (Korean emotional clone)
```python
from tools.tool_registry import registry
registry.discover()
voxcpm = registry._tools["voxcpm_tts"]

# 1) Anchor first
voxcpm.execute({
    "text": "<first segment text>",
    "voice_design": "(warm mature male narrator, deep and clear)",
    "emotion": "차분하고 신뢰감 있는 뉴스 앵커 톤",
    "device": "mps",
    "output_path": "projects/<name>/assets/audio/voxcpm_anchor.wav",
})

# 2) Batch clone (same anchor for every segment)
for i, text in enumerate(segments):
    voxcpm.execute({
        "text": text,
        "reference_audio": "projects/<name>/assets/audio/voxcpm_anchor.wav",
        "device": "mps",
        "output_path": f"projects/<name>/assets/audio/voxcpm_{i:03d}.wav",
    })
```

### qwen3_local (premium Korean timbre + clone)
```python
qwen3 = registry._tools["qwen3_tts_local"]

# Clone mode
qwen3.execute({
    "mode": "clone",
    "text": "<korean text>",
    "reference_audio": "<absolute path to ref wav>",
    "reference_text": "<transcript of ref>",
    "language": "Korean",
    "output_path": "out.wav",
})

# Or premium speaker (no reference needed)
qwen3.execute({
    "mode": "custom_voice",
    "text": "<korean text>",
    "speaker": "Sohee",
    "language": "Korean",
    "instruct": "잔잔하고 따뜻하게, 뉴스 앵커 톤으로",
    "output_path": "out.wav",
})
```

### omnivoice (multilingual + fast)
```python
omni = registry._tools["omnivoice_tts"]
omni.execute({
    "text": "<korean text>",
    "language": "ko",
    "reference_audio": "<absolute path to ref wav>",
    "ref_text": "<transcript of ref>",
    "device": "cpu",          # cpu stable, mps may hang
    "num_step": 16,           # 32 for max quality
    "output_path": "out.wav",
})
```

### ice012 (speed-1st)
```python
import torch
from transformers import AutoModelForCausalLM
import soundfile as sf

model = AutoModelForCausalLM.from_pretrained(
    "~/.cache/huggingface/hub/ice-012-audio",
    trust_remote_code=True, torch_dtype=torch.float16, device_map="mps",
)
# No separate tool in registry — call directly
audios = model.generate(
    text="<korean text>",
    ref_audio="<absolute path>",
    ref_text="<transcript>",
    language="Korean", speed=1.0,
)
sf.write("out.wav", audios[0], model.sampling_rate)
```

(ice012 has no registry wrapper. Load it once per session; reuse for all segments.)

### higgs_v2_mlx (Mac MLX, experimental)
```python
import os, soundfile as sf, subprocess
# 24kHz mono WAV required
REF_WAV = "/tmp/ref_24k.wav"
subprocess.check_call(
    ["ffmpeg","-y","-i","voice_samples_celebs/son_sukhee/tQzFIEEDh4U_0002.mp3",
     "-ar","24000","-ac","1","-c:a","pcm_s16le", REF_WAV],
    stderr=subprocess.DEVNULL,
)

from mlx_audio.tts.models.higgs_audio import HiggsAudioServer

server = HiggsAudioServer.from_pretrained(
    model_path=os.path.expanduser("~/.cache/huggingface/hub/higgs-mlx-q8"),
    codec_path=os.path.expanduser("~/.cache/huggingface/hub/higgs-mlx-codec"),
)

REF_TEXT = "<transcript of ref audio>"
result = server.generate(
    target_text="<korean text>",
    reference_audio_path=REF_WAV,
    reference_text=REF_TEXT,
    max_new_frames=200,   # 200=short, 300=medium. NEVER use default 900.
    temperature=0.7,
)
sf.write("out.wav", result.pcm, result.sampling_rate)  # 24 kHz mono
```

(Load once per session; reuse for all segments. ~5.6s initial load.)

## Selector Routing (tts_selector)

For automated routing, restrict `tts_selector` to the four engines:

```python
from tools.tool_registry import registry
registry.discover()
selector = registry._tools["tts_selector"]

# Quality-first, voxcpm
selector.execute({
    "text": "<text>",
    "preferred_provider": "voxcpm",
    "allowed_providers": ["voxcpm", "qwen3_local", "omnivoice", "ice012"],
    "output_path": "out.wav",
})

# Speed-first, ice012
selector.execute({
    "text": "<text>",
    "preferred_provider": "ice012",
    "allowed_providers": ["voxcpm", "qwen3_local", "omnivoice", "ice012"],
    "output_path": "out.wav",
})
```

`preferred_provider` is the primary intent; selector falls back through `allowed_providers` if the preferred one is blocked.

## Decision Log Convention (binding)

When choosing an engine for a Korean clone project, append to `decision_log`:

```json
{
  "category": "voice_selection",
  "subject": "Narration TTS provider",
  "selected": "<engine>",
  "options_considered": [
    {"engine": "voxcpm",    "mfcc_sim": 0.998, "rtf": 9.22, "selected_reason": "..."},
    {"engine": "qwen3_local", "mfcc_sim": 0.998, "rtf": 6.26, "selected_reason": "..."},
    {"engine": "omnivoice", "mfcc_sim": 0.998, "rtf": 3.79, "selected_reason": "..."},
    {"engine": "ice012",    "mfcc_sim": 0.997, "rtf": 1.86, "selected_reason": "..."}
  ],
  "rejected_because": "<why others weren't primary>"
}
```

If a voice decision changes mid-run, **append a new entry with same `(category, subject)` pair**, not edit the old one (per AGENT_GUIDE.md decision log rule).

## Bench Data

- Reference: `voice_samples_celebs/son_sukhee/tQzFIEEDh4U_0002.mp3` (8.28s, 손석희)
- Outputs: `projects/son-bench/audio/` (24 WAVs)
- Metrics: `projects/son-bench/_metrics.json`
- Methodology: MFCC-20 cosine similarity (proxy for speaker identity), Whisper-tiny transcribe, ffprobe for sr/duration

MFCC is a proxy; for absolute verification use `resemblyzer` (when installed) or `speechbrain/spkrec-xvect-voxceleb`.

## Common Pitfalls

1. **VoxCPM `prompt_text`** — Don't pass it for clone mode; the CLI rejects it without `--prompt-audio`.
2. **qwen3 long text** — Degrades over 1-2 sentences; split + concat.
3. **omnivoice mps hang** — Use `device="cpu"` (registered skill notes "MPS may hang on some models; CPU is stable").
4. **ice012 ref_audio path** — Must be absolute; relative paths fail silently.
5. **Mixing engines mid-video** — Don't. Voices differ in timbre; stick to one engine per project for voice consistency.
6. **Reference mismatch** — `reference_text` wrong by ≥30% drops SIM noticeably. Always Whisper first.
7. **higgs_v2_mlx output length** — Default `max_new_frames=900` produces 36s output regardless of input text. Always pass `max_new_frames=200-300` for typical Korean sentences. Long captions/timelines need pre-trim of the audio file.
8. **higgs_v2_mlx reference format** — Must be 24kHz mono WAV. mp3 or non-24kHz input silently fails or distorts.

## Related Skills

- `voxcpm-tts` — VoxCPM-specific workflow
- `qwen3-tts-local` — Qwen3 TTS workflow
- `tts-sample-unification` — Anchor sample consistency across segments
- `voice-sample-collector` — Harvesting natural human voice references
- `text-to-speech` — General TTS guide
- `mlx-audio` (the runtime Higgs v2 MLX port uses) — for any other MLX TTS experiments
