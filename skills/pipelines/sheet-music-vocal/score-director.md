# Score Director — Score Analysis Stage

Analyzes the musical metadata and structural parts of the incoming score file.

## Quality Bar
- Detects whether the input is a single-part lead sheet, piano reduction (grand staff), string quartet, or SATB choral score.
- Extracts global tempo (BPM), time signature, and key signature accurately.
- Identifies whether the score already contains lyric syllables across verses, or requires external lyric text mapping.
- Validates divisions and measure timings to guarantee drift-free blick conversion.

## Outputs
- `score_manifest`: JSON artifact specifying total measures, target melodic parts, verse count, and tempo profile.
