# Asset Director — Short-Form Factory

## When to Use
Produce all required audio and visual assets for the short-form video.

## Execution
1. **TTS Narration:** Generate sentence-by-sentence narration via VoxCPM2 (local emotional acting) or Edge-TTS, and measure real durations via ffprobe.
2. **Visual Assets:** Use `pexels_video` / `pexels_image` or `google_nano_banana` / `google_imagen` based on script search terms.
3. **Background Music:** Select high-energy, royalty-free BGM via `pixabay_music` or `google_music`.
4. **Output:** Schema-valid `asset_manifest` artifact.
