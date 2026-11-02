# Script Director - Audiobook Pipeline

## When To Use

Second stage. Converts the approved book scope into the reviewed **lines JSON** (the single source of truth for synthesis) and the canonical `script` artifact.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/script.schema.json` | Artifact validation |
| Prior artifact | `brief` | Scope and cast plan |
| Tool | `audiobook_builder` (`action: parse`) | Produces the first-draft lines JSON |

## Process

### 1. Parse

Call `audiobook_builder` with `action: parse`, `book_path`, `output_path: projects/<id>/artifacts/lines.json`, `chunk_limit: 120`. Each line has `i`, `speaker`, `kind`, `section`, `text`, `emotion`.

Kinds: `h1` book/chapter title, `h2` section heading (becomes a chapter marker), `p` first chunk of a paragraph, `c` continuation chunk (shorter gap).

### 2. Make The Text Speakable (edit lines.json)

TTS reads what is written. Fix before synthesis, never after:

- Numbers and units: write `50%` as `오십 퍼센트`, `7번` as `일곱 번`/`칠 번` according to context, `2024년` as `이천이십사 년`.
- Latin words, acronyms, symbols: spell as pronounced (`AI` -> `에이아이`, `DNA` -> `디엔에이`).
- Title lines such as `제1장` are misread; write `제일장`.
- Remove footnote marks, URLs, markdown, emoji.
- Keep each chunk to about 120 characters; split sentences, never words. Very short lines (under ~4 syllables) mispronounce - merge with a neighbour or lengthen.
- Keep `text` and the later subtitle/transcript identical; the Whisper check compares against `text`.

### 3. Assign Speakers And Emotion

- `speaker` values must match the approved cast plan exactly.
- `emotion` is a Korean natural-language cue passed to VoxCPM `--control`, e.g. `차분하고 묵직한 나레이션`, `긴박하고 낮게`, `차갑고 기계적인 시스템 안내 음성`. Vary by section mood, but keep it short (one phrase). Long or instruction-like emotion text can be read aloud by the model - the Whisper check will catch that.
- Narrator emotion should stay close to the anchor; large swings change timbre.

### 4. Write The Script Artifact

One `script.sections[]` entry per h2 section: `id`, `label` (heading), `text` (joined line text), `start_seconds`/`end_seconds` (estimated at 0.17 s per syllable plus gaps), `speaker_directions` (speakers present). `total_duration_seconds` = the sum. The lines JSON path goes in `metadata.lines_path`.

## Gate

Human approval required: show the heading list, the speaker/line counts, three sample lines per speaker and every number/foreign-word rewrite. Re-parse only if the source text changed; otherwise edit lines.json in place.
