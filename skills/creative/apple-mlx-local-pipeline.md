# Apple Silicon MLX Local Video Production Workflow

> Complete blueprint for running **100% offline, private, zero-cost AI video production on Apple Silicon (M1/M2/M3/M4)** using Apple's native **MLX Framework**, unified memory architecture, and Metal GPU acceleration.

---

## 1. Why MLX on Apple Silicon?

Apple MLX is an open-source machine learning framework engineered specifically for Apple Silicon processors. It achieves breakthrough speed and memory efficiency compared to PyTorch/CUDA by exploiting:
1. **Unified Memory Architecture (UMA):** CPU and GPU share the same ultra-high-bandwidth memory pool (up to 800 GB/s on Max/Ultra chips). Zero data copying between RAM and VRAM.
2. **Lazy Evaluation & Multi-Device Streams:** Computations are scheduled efficiently across CPU, GPU, and Neural Engine.
3. **Native 4-bit / 8-bit Quantization:** Runs large 7B~14B multimodal models inside 8GB~16GB RAM MacBooks without swapping.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Apple Silicon Unified Memory (UMA)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [mlx_lm] ─────────► Script & Scene Planning (Qwen 2.5 / EXAONE 3.5)    │
│  [voxcpm_tts] ─────► Emotional Acting Voiceover (MPS Acceleration)     │
│  [mlx_whisper] ────► Word-Level Timestamp Subtitles (Whisper Large-v3) │
│  [mlx_vlm] ────────► Frame QA & Automated Shot Tagging (Qwen2-VL)      │
│  [remotion] ───────► Frame-Accurate React Motion Graphics Render        │
│                                                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                      [100% Offline Master Video MP4]
```

---

## 2. Integrated Apple MLX Tool Suite

| Tool | Module Path | Capability | Highlights |
|---|---|---|---|
| **`mlx_whisper`** | `tools/analysis/mlx_whisper_transcriber.py` | Speech-to-Text & Subtitles | 5x faster than standard Whisper on Mac, word-level `.srt`/JSON sync |
| **`mlx_vlm`** | `tools/analysis/mlx_vlm_analyzer.py` | Multimodal Vision QA | Local Qwen2-VL / Pixtral inference for B-roll review & thumbnail analysis |
| **`mlx_lm`** | `tools/graphics/mlx_lm_writer.py` | Local Script & Storyboard LLM | Offline Qwen 2.5 / Llama 3.2 / EXAONE 3.5 for creative scripting |
| **`voxcpm_tts`** | `tools/audio/voxcpm_tts.py` | Emotional TTS (OpenBMB) | PyTorch MPS accelerated voice design and cloning |

---

## 3. End-to-End Apple MLX Production Sequence

### Step 1: Local Script Generation (`mlx_lm`)
Generate a retention-optimized script completely offline:
```python
from tools.graphics.mlx_lm_writer import MLXLMWriter

writer = MLXLMWriter()
result = writer.execute({
    "prompt": "Write a 60-second YouTube Short script about why black holes bend time. Include 3-second hook and 5 punchy scenes.",
    "model_path": "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "max_tokens": 800
})
script_text = result.data["response"]
```

### Step 2: Local Emotional Voiceover (`voxcpm_tts`)
Synthesize rich, expressive audio using Apple Silicon MPS:
```python
from tools.audio.voxcpm_tts import VoxCPMTTS

vox = VoxCPMTTS()
vox.execute({
    "text": script_text,
    "voice_design": "(deep, cinematic Korean narrator with philosophical warmth)",
    "emotion": "신비롭고 웅장하며 깊은 감동을 주듯이",
    "device": "mps",
    "output_path": "projects/<project_id>/assets/audio/narration.wav"
})
```

### Step 3: Blazing-Fast Subtitle Extraction (`mlx_whisper`)
Extract word-level timestamps on Apple Silicon Metal in seconds:
```python
from tools.analysis.mlx_whisper_transcriber import MLXWhisperTranscriber

whisper = MLXWhisperTranscriber()
stt_result = whisper.execute({
    "input_path": "projects/<project_id>/assets/audio/narration.wav",
    "model_path": "mlx-community/whisper-large-v3-turbo",
    "word_timestamps": True,
    "output_dir": "projects/<project_id>/assets/subtitles"
})
# Outputs: <name>_mlx_transcript.json and <name>_mlx_subtitles.srt
```

### Step 4: Local Visual B-Roll QA (`mlx_vlm`)
Verify visual composition of downloaded footage or generated stills:
```python
from tools.analysis.mlx_vlm_analyzer import MLXVLMAnalyzer

vlm = MLXVLMAnalyzer()
qa_result = vlm.execute({
    "image_path": "projects/<project_id>/assets/images/scene_01_frame.png",
    "prompt": "Is the text clearly legible? Does the color palette convey a cinematic cosmic mood?",
    "model_path": "mlx-community/Qwen2-VL-7B-Instruct-4bit"
})
print("Visual QA:", qa_result.data["response"])
```

### Step 5: Remotion Video Assembly
Assemble the video using Remotion with kinetic typography, audio waveform visualizers, and Pexels/NASA 4K footage.

---

## 4. Hardware Recommendations for Apple Silicon

| Mac Model | RAM | Recommended MLX Models | Production Tier |
|---|---|---|---|
| **MacBook Air / Pro (M1/M2/M3/M4)** | 8GB - 16GB | `Qwen2.5-3B-4bit`, `whisper-small-mlx`, `Qwen2-VL-2B-4bit` | Fast 1080p Shorts / Viral Clips |
| **MacBook Pro / Mac Mini** | 18GB - 36GB | `Qwen2.5-7B-4bit`, `whisper-large-v3-turbo`, `Qwen2-VL-7B-4bit` | 4K Broadcast Explainers & Documentaries |
| **Mac Studio / Mac Pro (Max/Ultra)** | 64GB - 192GB | `Qwen2.5-72B-4bit`, `Llama-3.3-70B-4bit`, full unquantized VLM | Studio-Tier Feature & Episodic Workflows |
