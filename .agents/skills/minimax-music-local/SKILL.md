---
name: minimax-music-local
description: MiniMax Music 3 local music generation on Apple Silicon MLX — open-weight song generation with lyrics, structured captions, and long-form output up to 5 minutes.
---

# MiniMax Music 3 — Local Open-Weight Music Generation (MLX)

MiniMax Music 3 (8B Global LLM + 0.6B Local LLM + Flow Matching) runs locally
on Apple Silicon via `mlx-audio`, generating complete songs with vocals and
structured arrangements. Zero API cost, fully offline.

## Tool

`minimax_music_local` (`tools/audio/minimax_music_local.py`, provider `minimax_local`).

## Usage

```python
from tools.audio.minimax_music_local import MiniMaxMusicLocal
t = MiniMaxMusicLocal()

# Instrumental background music
t.execute({
    "prompt": "Calm ambient piano, peaceful and reflective, soft pads",
    "duration_seconds": 30.0,
    "seed": 42,
    "output_path": "assets/music/bgm.wav",
})

# Song with vocals + lyrics
t.execute({
    "prompt": "A warm acoustic pop song with intimate female vocals, fingerpicked guitar",
    "lyrics": "[Verse]\nMorning light filtering through the pine\n[Chorus]\nSoftly the world begins to breathe",
    "duration_seconds": 60.0,
    "output_path": "assets/music/song.wav",
})
```

## Prompt Engineering

- **Caption** = global style: genre, BPM, key, mood, vocal details, arrangement.
- **Lyrics** = temporal structure with section tags: `[Intro]`, `[Verse]`,
  `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]`.
- **Instrumental**: omit lyrics (the tool auto-injects `[instrumental]`).
- **Structured caption** (3 sections) gives best control:
  1. Global Metadata — genre, BPM, key, emotional progression
  2. Vocal Details — gender, timbre, performance style, harmonies
  3. Arrangement — instruments, groove, bass, percussion, textures

## Notes

- Output: 32kHz 16-bit stereo WAV.
- `duration_seconds` up to ~300 (5 min).
- `steps` (default 30) controls flow-matching quality/speed tradeoff.
- Local MLX is slower than the API; first load downloads the ~6.5GB 4-bit model.
- For API-based generation (faster, needs key), use `minimax_music` instead.
