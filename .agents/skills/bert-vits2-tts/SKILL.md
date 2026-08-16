# Bert-VITS2 TTS (zh/en/ja + Korean)

Local, free multilingual TTS for OpenMontage via `tools/audio/bert_vits2_tts.py`
(provider `bert_vits2`). No API key. Two engines, selectable via `engine`:

| engine | base | languages | Korean path |
|--------|------|-----------|-------------|
| `multilingual` (default) | fishaudio/Bert-VITS2 v2.3 | zh, en, ja | ko → ja-substitution (`ko_to_kana`) |
| `korean` | jwj7140/Bert-VITS2-Korean | ko (native) | **g2pK** pronunciation + KoBERT, tones=0 |

## The Korean G2P core (`tools/audio/ko_g2p.py`)
Wraps **kyubyong/g2pK** — the standard Korean grapheme-to-phoneme library (Mecab
morphological context when available). This is the "대본 텍스트를 실제 소리
나는 대로 치환" preprocessing that TTS engines learn from:

```
"신을 신고 얼른 동사무소에 가서 혼인 신고 해라"
  -> "시늘 신꼬 얼른 동사무소에 가서 호닌 신고 해라"
```
Handles 연음(liaison), 구개음화(palatalization), 된소리/격음화(tensification),
number→Hangul reading, etc. Use `g2p()` anywhere script text must be converted
to pronunciation (TTS training data prep, phoneme-aware subtitle generation).

## Korean-native engine (recommended for ko)
- Repo: `tools/_bert_vits2_kr/` (cloned jwj7140/Bert-VITS2-Korean)
- G2P via `g2pk2` inside `text/korean.py`; KoBERT (`beomi/kcbert-large`) context;
  `language_tone_start_map = {"KO": 0}` — tones forced to 0 (Korean has no tones).
- The engine's inference deps + KoBERT: `python tools/_bert_vits2_kr/setup_bert_vits2_kr.py`
- **Model weights are not pre-hosted** — they come from training on your Korean
  dataset (the Nexon-style recipe below) or a community release. Drop
  `G_0.pth` + `config.json` into `tools/_bert_vits2_kr/models/`.

### Training a Korean model (Nexon-style recipe)
1. Dataset: `<wav_path>|<speaker>|KO|<script text>` list.
2. Preprocess: `resample.py` → `preprocess_text.py` → `spec_gen.py` → `bert_gen.py`
   (g2pK converts each utterance to pronunciation before BERT features).
3. Train: `train_ms.py` (config in `configs/`) — KO-only weights, no zh/en/ja.
4. Output `models/G_*.pth` + `config.json` → `tools/_bert_vits2_kr/models/`.

## Calling
```python
from tools.audio.bert_vits2_tts import BertVits2TTS
r = BertVits2TTS().execute({
    "engine": "korean",        # or "multilingual"
    "text": "여호와는 나의 목자",
    "language": "ko",
    "length_scale": 1.05,      # >1 slows speech
    "device": "cpu",           # cpu/mps/cuda
    "output_path": "projects/<id>/assets/audio/s01.wav",
})
```
Multilingual: `language` zh/en/ja natively; `ko` runs as JP after kana
substitution. Speakers come from `config.json → spk2id` (e.g. `派蒙_JP`), or
auto-pick the first speaker matching the language suffix.

## Status semantics
- `available` — code + weights present (currently: **all 4 languages verified on
  Mac CPU** — G_0.pth + JP/EN/ZH BERTs downloaded under `tools/_bert_vits2/`)
- `degraded` — code ready, weights missing (returns a clear error)
- `unavailable` — inference env not installed

## Verified on this machine (Aug 2026)
- ko `여호와는 나의 목자니…` 4.6s (hiragana 발음치환 → JP) · ja · en · zh all pass
- First inference is slow (~model load); warm with a short sentence before batching
- If the subprocess ever hangs at import, it is the old BERT download check —
  set `BERT_SKIP_CHECK=1` (runners already do this).

## Layer 3 pointer
- Multilingual engine: `tools/_bert_vits2/` (`run_infer.py`, `setup_bert_vits2.py`)
- Korean engine: `tools/_bert_vits2_kr/` (`run_infer_kr.py`, `setup_bert_vits2_kr.py`)
- G2P module: `tools/audio/ko_g2p.py`

## Tips
- First inference loads the model (multi-GB RAM on CPU); warm it with a short
  sentence before batching.
- For narration-led pipelines, route through `tts_selector` with
  `preferred_provider: "bert_vits2"` when a specific language/voice is needed.
- Supertonic (M1) remains the fastest Korean option when Bert-VITS2 models
  aren't downloaded yet.
