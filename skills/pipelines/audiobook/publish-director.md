# Publish Director - Audiobook Pipeline

## When To Use

Final stage. Packages the audiobook for the user. Default is a local export; any upload to a store, podcast host or channel is outward-facing and needs explicit approval for that destination.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/publish_log.schema.json` | Artifact validation |
| Prior artifacts | `render_report`, `final_review` | Files and verification |

## Process

1. Confirm `final_review.status` is `pass`.
2. Create `projects/<id>/exports/<slug>/` containing: the `.m4b`, the `.mp3`, `lines.json`, a `chapters.txt` (`mm:ss title` per marker) and a `README.txt` listing voices used (designed vs cloned) and the tool versions.
3. Metadata: title, author, album, chapter list. Add a cover image only if the user supplied one (no image generation in this pipeline).
4. State the disclosure: the narration is AI-generated (VoxCPM2). Recommend the user include that wherever they distribute it, and remind them that distributing a voiced adaptation of someone else's book needs the rights holder's permission.
5. `publish_log.entries[]`: `platform: "local_export"`, `status: "exported"`, `export_path`, timestamp. Only add other platforms if the user asked and approved.

## Gate

Human approval required before write. Offer next steps: more chapters (reuse anchors), speaker re-tagging for more character voices, or a video version via `novel-to-video`.
