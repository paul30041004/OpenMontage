# Idea Director - Audiobook Pipeline

## When To Use

First stage of the `audiobook` pipeline. The user hands over a book file (EPUB / TXT / MD, or a PDF converted to text) and wants it narrated. This stage turns that into a `brief`, a cast plan and a scope decision. It is also the pipeline's orchestration entry point: read `pipeline_defs/audiobook.yaml` first.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/brief.schema.json` | Artifact validation |
| Tool | `audiobook_builder` (`action: parse`) | Count lines/characters/speakers for estimates |
| Layer 3 | `.agents/skills/voxcpm-tts` | Voice design + clone rules (English `voice_design`, Korean `emotion`) |

## Process

### 1. Confirm The Source

- Accepted: `.epub`, `.txt`, `.md`. For PDF, extract text first (tell the user it needs a text layer; scanned PDFs need OCR).
- Ask once about rights: it must be the user's own text, licensed, or public domain. Do not proceed on an obvious pirated commercial book.
- Run `audiobook_builder` `parse` into the project folder as a dry run. Report chapters (h1/h2 count), line count, character count and detected speakers.

### 2. Estimate

Korean narration runs about 0.17 s per syllable, plus gaps. Use `total_chars * 0.17 * 1.15` seconds as `target_duration_seconds`. Synthesis takes roughly 20-25 s of wall time per line including verification, so state the real wait (lines x ~25 s).

### 3. Scope

- First run: ONE chapter. It proves voices and pacing cheaply. Only then queue the rest.
- Long books: one project per chapter or one per volume, sharing the same voice anchors (copy them in).

### 4. Cast Plan

For every speaker, record the voice source:

| Speaker | Typical voice source |
|---------|---------------------|
| narrator | designed from an English description, or cloned from a user reference clip |
| system | designed "cold, mechanical" voice, used for system notices |
| named character | designed per character; ask the user before inventing dialogue attribution |

If the user supplies a reference voice, it must be their own voice or one they have the right to clone.

Speaker attribution is not automatic. The parser treats paragraphs starting with `시스템 알림` / `[시스템]` as `system`, paragraphs starting with `[이름] ` as that character, everything else as `narrator`. Tell the user to tag dialogue in the source if they want character voices, or offer to tag it in the script stage.

### 5. Write The Brief

`brief.title` = book/chapter title; `hook` = first narrated line; `key_points` = chapter list; `tone` = reading style; `style` = "audiobook, local VoxCPM"; `target_platform` = `generic`; `target_duration_seconds` from step 2. Record the cast plan and rights confirmation in `decision_log`.

## Gate

Human approval required: source, scope (which chapters), cast plan, expected wait. Do not start voice work before approval.
