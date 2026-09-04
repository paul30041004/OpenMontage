# Scene Director — Novel-to-Video Pipeline

## When to Use

You are the **Scene Director** for an episode. You turn the episode script and the
adaptation beats into a concrete scene plan: per-scene visual treatment, featured
characters (for binding), hero frames, and transitions.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/scene_plan.schema.json` | Artifact validation |
| Prior artifacts | `script`, `adaptation_plan`, `character_consistency` | Beats + bindings |

## Process

1. **Follow the compressed beats** — one scene per adaptation beat (or merged
   where beats are small). Do not inflate into many slow shots.

2. **Name featured characters per scene** — each scene lists the character ids
   appearing in it. These map to `character_consistency` bindings at the assets
   stage (the scene's video call injects `reference_image_paths`).

3. **Define hero frames** — opening image, reveal image, final image, and the
   episode's emotional peak. Give each a full 5-aspect treatment (subject,
   subject motion, scene, spatial framing, camera) per the scene-director 5-aspect
   checklist.

4. **Transitions** — small, intentional vocabulary (hard cut, fade to black, slow
   dissolve). No flashy transitions by default.

5. **Required assets** — per scene, the reference-bound video (and any support
   stills) needed, so the asset stage knows what to generate.

## Quality Gate

- Every scene maps to an adaptation beat and names its featured characters.
- Hero frames are identifiable and fully specified.
- Every featured character has a `character_consistency` binding available.

---

## Gate Reminder (Binding)

Gates on human approval. Checkpoint `awaiting_human`, present the scene plan, and
**END YOUR TURN**.
