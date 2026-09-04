# Character Director — Novel-to-Video Pipeline

## When to Use

You are the **Character Director** for a long-form video adaptation. You turn the
`adaptation_plan.cast` into a consistent, filmable set of characters using the
`character_consistency` layer: anchor reference frames + video-gen bindings, so
one character keeps the same look across every scene and episode.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/character_consistency.schema.json` | Artifact validation |
| Prior artifact | `adaptation_plan` (cast) | Character source |
| Tool | `character_consistency_builder` | Anchor + binding generation |
| Skill | `.agents/skills/character-consistency/SKILL.md` | Pattern reference |

## Process

### Step 1: Scope to the Episode Being Produced

You do not need anchors for the entire cast at once. Identify which cast members
appear in the **current episode** (the one the Script Director covered). Only
those need anchor frames now. The rest can be added when their episode is made.

### Step 2: Normalize Character Specs

For each in-scope cast member, confirm:
- `appearance` is identity-anchoring (reused verbatim — never rephrased)
- `role` matches the narrative function
- `reference_prompt` — if absent, the builder composes it from appearance + style

### Step 3: Generate Anchor Frames

Call `character_consistency_builder` with `operation: "generate_frames"`:

```python
builder.execute({
    "operation": "generate_frames",
    "characters": [
        {"id": c["id"], "role": c["role"], "appearance": c["appearance"]}
        for c in in_scope_cast
    ],
    "style": {"visual_style": "<the episode's visual language>"},
    "views": ["front"],                 # add "three-quarter" for hero characters
    "aspect_ratio": "<episode aspect ratio>",
    "output_dir": "projects/<project>/assets/characters",
    "output_path": "projects/<project>/artifacts/character_consistency.json",
})
```

This renders each character's anchor frame(s) and fills
`reference_frames` + `binding_hints.reference_image_paths`.

### Step 4: QA the Anchors (critical)

Inspect every anchor frame before approving:
- Does the face/build/outfit match the intended identity?
- Do different views of the same character look like the SAME person?
- Is the style consistent with the episode's visual language?

A bad anchor propagates to every bound scene. Regenerate before approving, never
after. Never mix anchors from different runs mid-episode.

### Step 5: Hand Off Bindings

The `character_consistency` artifact now carries, per character:
- `binding_hints.reference_image_paths` — passed as `reference_image_paths` to
  video generation for every scene featuring that character
- `binding_hints.preferred_providers` — e.g. higgsfield, seedance, veo
- `binding_hints.first_frame_path` — canonical first-frame for scene openings

Downstream stages (scene_plan, assets) consume these bindings directly.

## Quality Gate

- Every scene character in the episode has a working `reference_image_paths` binding.
- Anchors pass identity QA.
- No character appears in scene_plan without a corresponding cast entry.

## Common Pitfalls

- **Rephrasing appearance** across scenes — the model drifts; embed it verbatim.
- **One anchor for all characters** — each character needs its OWN anchor.
- **Skipping QA** — a wrong-face anchor poisons the whole episode.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review
passes: checkpoint with `status="awaiting_human"`, present the anchor contact
sheet (the Backlot board renders it), and **END YOUR TURN**.
