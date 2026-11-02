# Idea Director — Short-Form Factory

## When to Use
First stage in `short-form-factory`. Establish the viral premise, core curiosity gap, 3-second hook, and 9:16 vertical delivery strategy.

## Runtime Selection (MANDATORY — present both, never silently default)

This pipeline has no separate proposal stage, so the idea stage locks `render_runtime`; `video_compose` routes by it at compose. Per AGENT_GUIDE.md → "Present Both Composition Runtimes (HARD RULE)": check `video_compose.get_info()["render_engines"]` and, when both are available, **present both** and wait for approval. For *this* short (9:16, word-by-word karaoke subtitles over stock/AI video), give each a one-sentence fit and tradeoff:

- **hyperframes** — HTML/CSS/GSAP compositions via `hyperframes_compose`, which this pipeline's compose stage declares as a tool. Fit: kinetic, text-led vertical shorts. Tradeoff: the runtime must pass `hyperframes_compose` `operation="doctor"` on this machine first.
- **remotion** — React compositions through `video_compose`. Fit: the stock cinematic/caption components. Tradeoff: heavier render, and a caption look that differs from a hand-authored HTML one.

Recommend `hyperframes` as the first candidate if `doctor` passes and `remotion` otherwise, and say that this is the basis. Record a `render_runtime_selection` decision in `decision_log` with BOTH runtimes in `options_considered` and the rejected one's `rejected_because`. If only one runtime is installed, say so explicitly and record the other as `rejected_because: "runtime not available on this machine"`. If the user changes it later, append a new entry with the same category and subject.

## Key Principles
1. **The 3-Second Rule:** First 3 seconds must create an irresistible curiosity gap or visual jolt.
2. **Platform Fit:** Optimize for YouTube Shorts, TikTok, and Instagram Reels (9:16 aspect ratio).
3. **Pacing:** Target duration 30-50 seconds, 150-180 words/min speech tempo.
4. **Output:** Schema-valid `brief` and `decision_log`.
