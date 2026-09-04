"""Audio8 TTS 0.1B text-to-speech and zero-shot voice cloning tool.

Audio8 TTS Preview 0.1B is a compact, ultra-efficient (~0.17B parameters)
autoregressive TTS model supporting speech synthesis and zero-shot voice cloning
across Chinese, English, Korean, Japanese, and European languages.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

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

log = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "Audio8/Audio8-TTS-Preview-0.1b"


def _patch_transformers_cache() -> None:
    """Ensure compatibility with both Transformers v4 and v5 cache architectures."""
    try:
        import transformers.cache_utils as cu
        import transformers.models.falcon_h1.modeling_falcon_h1 as fh1

        if not hasattr(fh1, "FalconHybridMambaAttentionDynamicCache"):
            class FalconHybridMambaAttentionDynamicCache(cu.DynamicCache):
                def __init__(self, config=None, batch_size=None, dtype=None, devices=None, **kwargs):
                    super().__init__(config=config)

            fh1.FalconHybridMambaAttentionDynamicCache = FalconHybridMambaAttentionDynamicCache
    except Exception as e:
        log.debug("Cache patch skipped or unnecessary: %s", e)


class Audio8TTS(BaseTool):
    name = "audio8_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "audio8"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:transformers", "python:torch", "python:soundfile"]
    install_instructions = (
        "Install Audio8 dependencies:\n"
        "  pip install torch torchaudio transformers soundfile safetensors\n"
        "Model checkpoint 'Audio8/Audio8-TTS-Preview-0.1b' is downloaded automatically from Hugging Face."
    )
    agent_skills = ["audio8-tts", "text-to-speech"]

    capabilities = [
        "text_to_speech",
        "zero_shot_voice_cloning",
        "voice_cloning",
        "multilingual_tts",
    ]
    supports = {
        "voice_cloning": True,
        "zero_shot": True,
        "multilingual": True,
        "local_inference": True,
        "mps_acceleration": True,
    }
    best_for = [
        "ultra-lightweight local zero-shot voice cloning (only ~170M params)",
        "low-latency local TTS without large VRAM requirements",
        "natural Korean, English, and Chinese speech generation",
    ]
    not_good_for = [
        "low-memory machines with <4GB RAM",
    ]

    fallback_tools = ["voxcpm_tts", "edge_tts", "google_tts"]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize into speech.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to reference WAV/MP3 audio file for zero-shot voice cloning.",
            },
            "reference_text": {
                "type": "string",
                "description": "Transcript matching the reference audio to improve cloning fidelity.",
            },
            "model_id": {
                "type": "string",
                "default": DEFAULT_MODEL_ID,
                "description": "Hugging Face model repository ID.",
            },
            "temperature": {
                "type": "number",
                "default": 0.7,
                "minimum": 0.1,
                "maximum": 1.5,
                "description": "Sampling temperature.",
            },
            "top_p": {
                "type": "number",
                "default": 0.9,
                "minimum": 0.1,
                "maximum": 1.0,
            },
            "top_k": {
                "type": "integer",
                "default": 50,
                "minimum": 1,
            },
            "max_new_tokens": {
                "type": "integer",
                "default": 256,
                "description": "Maximum generated audio tokens.",
            },
            "device": {
                "type": "string",
                "enum": ["auto", "mps", "cuda", "cpu"],
                "default": "auto",
            },
            "output_path": {
                "type": "string",
                "description": "Output path where the generated audio should be written (.wav or .mp3).",
            },
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=4096, vram_mb=2048, disk_mb=1500)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout", "out of memory"])

    def get_status(self) -> ToolStatus:
        try:
            import soundfile  # noqa: F401
            import torch  # noqa: F401
            import transformers  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.DEGRADED

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        text_len = len(inputs.get("text", ""))
        return max(3.0, text_len * 0.1)

    def _resolve_device(self, requested: str) -> str:
        import torch
        if requested and requested != "auto":
            return requested
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text is required for speech synthesis")

        _patch_transformers_cache()

        try:
            import soundfile as sf
            import torch
            from transformers import AutoModel, AutoProcessor
        except ImportError as exc:
            return ToolResult(
                success=False,
                error=f"Missing dependencies for Audio8 TTS: {exc}. {self.install_instructions}",
            )

        model_id = inputs.get("model_id", DEFAULT_MODEL_ID)
        device_str = self._resolve_device(inputs.get("device", "auto"))
        device = torch.device(device_str)
        dtype = torch.bfloat16 if device_str in ("cuda", "mps") else torch.float32

        out_path = Path(inputs.get("output_path", "audio8_output.wav"))
        out_path.parent.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        try:
            processor = AutoProcessor.from_pretrained(
                model_id,
                trust_remote_code=True,
            )
            model = AutoModel.from_pretrained(
                model_id,
                trust_remote_code=True,
                torch_dtype=dtype,
            ).eval().to(device)

            ref_audio = inputs.get("reference_audio")
            ref_text = inputs.get("reference_text")

            proc_kwargs: dict[str, Any] = {
                "text": [text],
                "return_tensors": "pt",
            }
            if ref_audio and Path(ref_audio).is_file():
                proc_kwargs["reference_audio"] = [str(ref_audio)]
                if ref_text:
                    proc_kwargs["reference_text"] = [ref_text]

            model_inputs = processor(**proc_kwargs)
            model_inputs = {name: val.to(device) for name, val in model_inputs.items()}

            gen_kwargs = {
                "max_new_tokens": inputs.get("max_new_tokens", 256),
                "temperature": float(inputs.get("temperature", 0.7)),
                "top_p": float(inputs.get("top_p", 0.9)),
                "top_k": int(inputs.get("top_k", 50)),
                "do_sample": True,
                "return_dict_in_generate": True,
            }

            with torch.inference_mode():
                output = model.generate(**model_inputs, **gen_kwargs)
                waveforms, waveform_lengths = model.decode_audio(output.codes)

            audio_data = waveforms[0, : int(waveform_lengths[0])].float().cpu().numpy()
            sample_rate = getattr(model.config, "codec_sample_rate", 44100)
            sf.write(str(out_path), audio_data, sample_rate)

        except Exception as exc:
            log.exception("Audio8 TTS generation failed: %s", exc)
            return ToolResult(
                success=False,
                error=f"Audio8 TTS generation failed: {exc}",
            )

        dur = None
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = float(probe.stdout.strip())
        except Exception:
            dur = None

        elapsed = round(time.time() - start_time, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "audio8",
                "model_id": model_id,
                "output": str(out_path),
                "duration_seconds": dur,
                "device": device_str,
                "zero_shot_cloned": bool(ref_audio),
            },
            artifacts=[str(out_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
        )
