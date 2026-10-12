# Code-Video Proxy — Layer 2 Skill

CodeVideoModel-style motion control for AI video generation: a deterministic,
editable Three.js scene is rendered into a short **proxy clip + first-frame
still**, then bound into `video_selector` (`operation="reference_to_video"`).
The proxy carries camera trajectory and object motion; the diffusion model
carries photoreal look. Never present the proxy itself as final footage.

## When to Use

- Motion-required briefs where text-to-video drifts: tracking shots, orbits,
  dolly moves, multi-object choreography, repeatable camera language.
- Any `cinematic` / `animation` run whose asset stage lists `threejs_proxy`.
- Do NOT use for dialogue close-ups, lip-sync, or physics sims (proxy has no
  articulated characters or dynamics).

## Workflow

### 1. Plan the shot (agent-owned)

Write the shot prompt first (subject + action + camera + environment +
lighting — same 5-aspect vocabulary as `creative/video-gen-prompting.md`),
then translate it into a `scene_spec`:

- `objects[]`: `box | sphere | cylinder | cone | torus | plane | car` with
  `position / rotation / size / color / metalness / roughness` and
  `motion: static | linear{from,to,t0,t1} | circular{center,radius,height,speed,phase}`.
  `car` is a stylized primitive (body + cabin + spinning wheels), not a model.
- `camera`: `keys[{t,pos,look}]` (strictly increasing, first `t=0`, last
  `t=duration`) or `orbit{target,radius,height,revolutions}`. Cap: 40 keys.
- `shot_spec`: `duration` 1–15s (prefer 4–10s; providers bill proxy seconds),
  `width/height`, `fps` 12/24/30. `seed` fixed per project for reproducibility.
- Read Layer 3 `threejs-fundamentals` / `threejs-animation` before authoring
  motion, `threejs-world-generation` for spec discipline.

### 2. Build the proxy

```python
threejs_proxy.execute({
    "operation": "build",
    "prompt": "<shot prompt>",
    "shot_spec": {"duration": 6, "width": 1280, "height": 720, "fps": 24},
    "scene_spec": {"objects": [...], "camera": {...}},
    "seed": 7,
    "output_path": "projects/<id>/assets/proxy/<shot>/",
})
```

- `operation="validate"` first for complex specs (returns normalized spec +
  report, writes nothing).
- The workspace (`index.html` + `scene.js` + `scene.json`) is editable and
  committed to the project dir; re-render by re-running `build` with the same
  seed. Never hand-edit `renders/` outputs.
- If `rendered` is False (no Chrome/FFmpeg), render later via
  `video_compose` / `hyperframes_compose` on the workspace — do not silently
  substitute stock footage for the approved proxy move.

### 3. Review the proxy (gate)

- Play `proxy_video`: camera move and object motion must read in the first
  2 seconds. Check `reference_frame`: hero subject framed, no clipping.
- Register in `asset_manifest` as `type: "motion_proxy"` with
  `source_tool: "threejs_proxy"`, seed, duration, workspace + artifact paths.
- Keep the `motion_proxy.json` artifact alongside; its `provider_hints`
  carry the exact binding paths.

### 4. Bind into video generation

```python
video_selector.execute({
    "operation": "reference_to_video",
    "prompt": "<final look prompt; cite proxy as motion control>",
    "reference_video_paths": ["<motion_proxy.provider_hints.reference_video_paths[0]>"],
    "reference_image_paths": ["<motion_proxy.provider_hints.reference_image_paths[0]>"],
    "preferred_provider": "minimax | seedance | kling_official | wan | runway | atlas",
    "output_path": "projects/<id>/assets/video/<shot>.mp4",
})
```

- Prefer `h3_max_video` / `minimax_video` for the CodeVideoModel-native path
  (code video + reference image + prompt); read Layer 3 `minimax-h3` before
  writing H3 prompts (prompt must cite Image/Video indices).
- Keep proxy ≤15s total; chain longer moves in `edit`, not in one proxy.
- Record the provider + model + binding paths in `decision_log`
  (`category: "provider_selection"`); re-log on any swap per AGENT_GUIDE.md.

## Quality Bar

- Proxy motion matches `scene_plan` camera beats frame-accurately; drift means
  fix the spec, not the prompt.
- Final clip preserves the proxy's trajectory; if the model ignores the
  proxy, escalate (provider swap) rather than re-rendering the proxy louder.
- Determinism: same seed + same spec = same proxy. Prove it once per project
  by rebuilding one shot.
