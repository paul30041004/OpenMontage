# Publish Director — Novel-to-Video Pipeline

## When to Use

You are the **Publish Director** for an episode. You package the finished episode
and queue the remaining episodes of the adaptation.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/publish_log.schema.json` | Artifact validation |
| Prior artifacts | `render_report`, `final_review`, `adaptation_plan` (optional), `script` (optional) | Output + plan |

## Process

1. **Hero export** — the episode MP4, clearly labeled with index, title, and
   source span (e.g. `ep01-the-flood-chapters-1-3.mp4`).

2. **Episode metadata** — title, description, chapters, tags, thumbnail concept
   featuring the lead character with identity intact.

3. **Remaining episodes** — list the next episodes from `adaptation_plan` as a
   production queue (index, title, source span) so the user can request them in
   sequence.

4. **Distribution notes** — aspect ratio, platform, visibility, and any
   limitations surfaced honestly.

## Quality Gate

- Hero export clearly labeled; derivative exports labeled by purpose; metadata
  fits the tone; remaining episodes listed for follow-up production.

---

## Gate Reminder (Binding)

Gates on human approval (`human_approval_default: true`). Checkpoint
`awaiting_human`, present the export package + episode queue, and **END YOUR TURN**.
