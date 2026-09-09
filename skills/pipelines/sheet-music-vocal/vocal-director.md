# Vocal Director — Vocal Generation Stage

Oversees the translation of notes, durations, pitch bends, and syllables into Synthesizer V Pro (.svp) projects.

## Execution Rules
1. **Octave Guard**:
   Enforce vocal range limits for each part to avoid unnatural screeching or sub-bass dropouts:
   - Soprano: A3 - D6 (MIDI 57 - 86)
   - Alto: D3 - F5 (MIDI 50 - 77)
   - Tenor: A2 - C5 (MIDI 45 - 72)
   - Bass: D2 - F4 (MIDI 38 - 65)
2. **Melisma Preservation**:
   Never blindly stamp external syllables on slur or melisma notes (`-`). Keep sustained vowel extensions clean.
3. **Natural Phrasing & Breath Sounds**:
   When rests >= 0.75 beats appear between lyrical phrases, insert natural aspiration notes (`br`) so virtual singers breathe realistically.
4. **Voice Assignment**:
   Bind installed high-tier AI voices to each role (e.g. Soprano: SOLARIA II, Alto: SAROS II, Tenor: Kevin 2, Bass: ASTERIAN II).
5. **Automation**:
   Use `synthv_runner` to inject the output directory and filename into `renderConfig`, opening Synthesizer V Studio for immediate 1-click rendering.
