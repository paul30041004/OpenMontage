# Subtitles Director — Presentation Subtitles Stage

Translates score timestamps and lyric syllables into broadcast-ready FreeShow (.json) presentation slides.

## Quality Bar
- Group syllables into smart 2-line phrases per slide using natural punctuation, musical rests, and cadence boundaries.
- Convert division timestamps into millisecond accuracy (`time_ms`, `time_end_ms`).
- Strip verse numerical prefixes (`1.`, `2.`, `3.`) to prevent screen clutter.
- Maintain full UTF-8 encoding for hangul characters to prevent encoding corruption.
