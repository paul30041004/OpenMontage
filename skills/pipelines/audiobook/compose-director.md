# Compose Director - Audiobook Pipeline

## When To Use

Fourth stage. Joins the approved line WAVs into the final audiobook files.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json`, `final_review.schema.json` | Artifact validation |
| Prior artifacts | `asset_manifest`, `script` | Line WAVs and lines.json |
| Tool | `audiobook_builder` (`action: assemble`) | Gaps, loudness, chapters, encode |

## Process

### 1. Assemble

`audiobook_builder` `action: assemble` with `lines_path`, `work_dir` (the folder holding the line WAVs), `output_path: projects/<id>/renders/<slug>` (extensions are added), `title`, `author`, `target_lufs: -19`, `bitrate: 96k`.

Built-in gap rules (seconds): 1.0 before an h2 heading, 0.6 after one, 0.5 around system lines, 0.35 between chunks of one paragraph, 0.7 between paragraphs. No music is added; an audiobook stays voice-only unless the user explicitly asks for ambience.

Chapter markers: one per `h1`/`h2` line, in order. The `.m4b` carries them; the `.mp3` carries title/artist/album tags only.

### 2. Verify (mandatory before final_review)

- `ffprobe -show_chapters` chapter count equals the number of h1+h2 lines.
- Duration within 5% of the sum of line durations plus gaps.
- Integrated loudness (`ebur128`) within 1 LU of -19 and true peak at or below -2 dB.
- Listen to (or at least probe) the first 10 seconds, one system line, and the last 10 seconds.

### 3. Artifacts

`render_report.outputs[]`: one entry per file with `format` (`m4b`/`mp3`), `audio_codec` (`aac`/`mp3`), `resolution: "audio-only"`, `duration_seconds`, `file_size_bytes`. Put chapters and LUFS in `metadata`.

`final_review`: `status` pass/revise/fail; `technical_probe` from ffprobe; the visual and subtitle checks are `not_applicable` for audio-only (state it, do not fake them); `audio_spotcheck` lists what you actually checked. If `revise`, go back to assets (re-synthesize lines) rather than patching the mix.

## Gate

Not human-gated. Present the files and probe results to the user before publish.
