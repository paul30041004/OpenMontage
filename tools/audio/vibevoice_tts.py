"""Microsoft VibeVoice Realtime 0.5B TTS tool for OpenMontage.

Wraps Microsoft's VibeVoice-Realtime-0.5B model — an ultra-lightweight,
real-time text-to-speech model with ~200ms first audible latency,
long-form generation (up to 10 minutes), and multilingual support (including Korean).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class VibeVoiceTTS(BaseTool):
    name = "vibevoice_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "vibevoice"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:transformers", "python:torch"]
    install_instructions = (
        "Install Microsoft VibeVoice:\n"
        "  git clone https://github.com/microsoft/VibeVoice.git\n"
        "  cd VibeVoice && pip install -e .[streamingtts]\n"
        "Model weights will auto-download from HuggingFace (microsoft/VibeVoice-Realtime-0.5B)."
    )
    agent_skills = ["vibevoice", "text-to-speech"]

    capabilities = [
        "text_to_speech",
        "streaming_tts",
        "realtime_voice",
        "multilingual_tts",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "streaming": True,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "ultra-low-latency real-time TTS (~200ms TTFA on Apple Silicon M-series)",
        "lightweight 0.5B model footprint (< 1GB VRAM/RAM)",
        "long-form narrative synthesis (up to 10 minutes) without truncation",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize into speech."
            },
            "speaker_name": {
                "type": "string",
                "default": "Carter",
                "description": "Speaker voice timbre (e.g. 'Carter', 'Default', or Korean experimental speaker)."
            },
            "language": {
                "type": "string",
                "enum": ["en", "kr", "ja", "de", "fr", "es", "it", "nl", "pl", "pt", "auto"],
                "default": "auto",
                "description": "Spoken language code (e.g. 'kr' for Korean, 'en' for English)."
            },
            "model_path": {
                "type": "string",
                "default": "microsoft/VibeVoice-Realtime-0.5B",
                "description": "Hugging Face model repository ID or local weights path."
            },
            "device": {
                "type": "string",
                "enum": ["mps", "cpu", "cuda"],
                "default": "mps" if sys.platform == "darwin" else "cpu",
                "description": "Inference device (mps for Apple Silicon, cuda for Nvidia, cpu fallback)."
            },
            "output_path": {
                "type": "string",
                "description": "File path to save the generated audio (WAV)."
            }
        }
    }

    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=2048, vram_mb=1024, disk_mb=2000)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])

    def _get_ffprobe(self) -> str:
        for c in ["ffprobe", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffprobe", "/opt/homebrew/bin/ffprobe"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffprobe"

    def get_status(self) -> ToolStatus:
        """Check if VibeVoice package or transformers environment is available."""
        try:
            import torch
            import transformers
            return ToolStatus.AVAILABLE
        except Exception:
            return ToolStatus.DEGRADED

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = params.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="합성할 텍스트(text)가 비어있습니다.")

        out_path = params.get("output_path")
        if not out_path:
            out_path = f"vibevoice_{int(time.time())}.wav"

        out_file = Path(out_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        speaker = params.get("speaker_name", "Carter")
        lang = params.get("language", "auto")
        model_path = params.get("model_path", "microsoft/VibeVoice-Realtime-0.5B")
        device = params.get("device", "mps" if sys.platform == "darwin" else "cpu")

        # Python execution script for VibeVoice inference
        script_code = f"""
import sys, os, time, copy, torch
from pathlib import Path
from vibevoice.modular.modeling_vibevoice_streaming_inference import VibeVoiceStreamingForConditionalGenerationInference
from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor

text = {repr(text)}
out_path = {repr(str(out_file))}
model_id = {repr(model_path)}
speaker = {repr(speaker)}
lang = {repr(lang)}
device = {repr(device)}

try:
    # Resolve voice preset
    repo_root = Path({repr(str(Path(__file__).resolve().parent.parent.parent))})
    preset_roots = [
        repo_root / "tools" / "_vibevoice" / "voices",
        Path("tools/_vibevoice/voices"),
    ]
    voice_file = None
    if "kr" in speaker.lower() or "korean" in speaker.lower() or lang == "kr" or any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in text):
        for pr in preset_roots:
            cand = pr / "kr" / "kr-Spk2_woman.pt"
            if cand.exists():
                voice_file = str(cand)
                break

    if not voice_file:
        for pr in preset_roots:
            if pr.exists():
                for pt in pr.rglob("*.pt"):
                    voice_file = str(pt)
                    break

    if not voice_file:
        raise FileNotFoundError("VibeVoice voice preset (.pt) not found.")

    processor = VibeVoiceStreamingProcessor.from_pretrained(model_id)
    model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        device_map=None,
        attn_implementation='sdpa'
    )
    model.to(device)
    model.eval()
    model.set_ddpm_inference_steps(num_steps=5)

    cached_prompt = torch.load(voice_file, map_location=device, weights_only=False)

    inputs = processor.process_input_with_cached_prompt(
        text=text,
        cached_prompt=cached_prompt,
        padding=True,
        return_tensors='pt',
        return_attention_mask=True
    )
    for k, v in inputs.items():
        if torch.is_tensor(v):
            inputs[k] = v.to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=None,
            cfg_scale=1.5,
            tokenizer=processor.tokenizer,
            generation_config={{"do_sample": False}},
            verbose=False,
            all_prefilled_outputs=copy.deepcopy(cached_prompt)
        )

    processor.save_audio(outputs.speech_outputs[0], output_path=out_path)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
"""
        python_bin = "/Users/paul/Documents/OpenMontage/.venv/bin/python"
        if not os.path.exists(python_bin):
            python_bin = sys.executable

        try:
            res = subprocess.run(
                [python_bin, "-c", script_code],
                capture_output=True,
                text=True,
                timeout=180
            )
            if res.returncode != 0 or not out_file.exists():
                return ToolResult(
                    success=False,
                    error=(
                        f"VibeVoice 합성 실패: {res.stderr.strip()}\n"
                        f"{self.install_instructions}"
                    )
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="VibeVoice 생성이 180초 타임아웃을 초과했습니다.")
        except Exception as e:
            return ToolResult(success=False, error=f"VibeVoice 실행 오류: {e}")

        # Probe duration
        duration_sec = 0.0
        try:
            cmd = [
                self._get_ffprobe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(out_file)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                duration_sec = float(res.stdout.strip())
        except Exception:
            pass

        return ToolResult(
            success=True,
            data={
                "provider": "vibevoice",
                "model": model_path,
                "speaker": speaker,
                "language": lang,
                "device": device,
                "output_path": str(out_file),
                "duration_seconds": round(duration_sec, 2),
                "file_size": out_file.stat().st_size,
                "latency_seconds": round(time.time() - start_time, 2)
            },
            artifacts=[str(out_file)]
        )
