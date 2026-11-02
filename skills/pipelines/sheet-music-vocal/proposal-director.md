# Proposal Director — Sheet Music & Vocal Pipeline

Second stage, after `score_analysis`. You know the score's parts, tempo and lyric language by now; this stage turns that into a plan the user approves **before** any vocal is synthesized or video rendered.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Prior artifact | `score_manifest` | Parts, verses, tempo, lyric language |
| Schema | `schemas/artifacts/proposal_packet.schema.json`, `decision_log.schema.json` | Artifact validation |

## Key Deliverables

1. **`proposal_packet.json`**
   - Deliverable: solo lead vocal or 4-part SATB virtual choir (confirm with the user; do not infer from the score alone).
   - Voice database per part (e.g. SOLARIA II, SAROS II, Kevin 2, ASTERIAN II as listed in `vocal-director`).
   - Output format: 16:9 presentation video or 9:16 vertical short.
   - Master target: -14 LUFS, plus the acoustic-space choice (church / hall).
   - `production_plan.render_runtime`: locked here, per the Runtime Selection section below.
   - Cost: vocal synthesis and mastering run locally, so the default budget is $0; state anything that would not.
2. **`decision_log.json`** — entries for deliverable, voice databases, and `render_runtime_selection`.

## Runtime Selection (MANDATORY — present both, never silently default)

The compose stage renders video through `video_compose`, which routes by `edit_decisions.render_runtime`, locked at this stage. Per AGENT_GUIDE.md → "Present Both Composition Runtimes (HARD RULE)": check `video_compose.get_info()["render_engines"]` and, when both are available, **present both** and wait for approval. For *this* piece (lyric cards synchronized to a sung track), give each a one-sentence fit and a one-sentence tradeoff:

- **remotion** — React compositions. Fit: reuses OpenMontage's stock scene and caption components. Tradeoff: heavier per-frame render, and lyric timings from `subtitle_manifest` must be mapped into props.
- **hyperframes** — HTML/CSS/GSAP compositions via `hyperframes_compose`. Fit: typography-led lyric cards are authored directly in HTML/CSS. Tradeoff: the runtime must pass `hyperframes_compose` `operation="doctor"` on this machine, and the same `subtitle_manifest` timing mapping is needed.

Neither route reads the FreeShow subtitle JSON natively, so do not promise frame-accurate sync from the format alone. Recommend whichever runtime renders one lyric card plus a few seconds of the mastered audio correctly in a quick sample, and say that this is the basis. Record a `render_runtime_selection` decision in `decision_log` with BOTH runtimes in `options_considered` and the rejected one's `rejected_because`. If only one runtime is installed, say so explicitly and record the other as `rejected_because: "runtime not available on this machine"`. If the user changes it later, append a new entry with the same category and subject.

## Human Gate

This stage has `human_approval_default: true`. Present the plan, the runtime options and the cost, then end the turn at `awaiting_human`.
