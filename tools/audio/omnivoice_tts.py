"""OmniVoice TTS tool — 600+ 언어 zero-shot voice cloning/design (Apple Silicon).

OmniVoice (k2-fsa) is a state-of-the-art massively multilingual zero-shot TTS
model. Supports voice cloning (reference audio) and voice design (speaker
attributes). Runs locally on Apple Silicon (MPS) or CPU.

Model: k2-fsa/OmniVoice (~612MB safetensors).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class OmniVoiceTTS(BaseTool):
    name = "omnivoice_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "omnivoice"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:omnivoice", "python:torch", "python:soundfile"]
    install_instructions = (
        "pip install omnivoice\n"
        "Requires: torch>=2.4, torchaudio>=2.4. Apple Silicon (MPS) or CPU."
    )
    agent_skills = ["text-to-speech", "tts-sample-unification"]

    capabilities = [
        "tts_multilingual",
        "voice_clone",
        "voice_design",
        "zero_shot_tts",
        "600_languages",
    ]

    supports = {
        "voice_cloning": True,
        "voice_design": True,
        "multilingual": True,
        "offline": True,
        "apple_silicon": True,
    }

    best_for = [
        "Zero-shot voice cloning from a 3-10s reference audio",
        "600+ language multilingual TTS",
        "Voice design via speaker attributes (gender/age/pitch/accent)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize.",
            },
            "language": {
                "type": "string",
                "description": "Language code (e.g. 'ko', 'en', 'ja', 'zh'). Auto-detect if omitted.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to a 3-10s WAV of the target voice (voice cloning mode).",
            },
            "ref_text": {
                "type": "string",
                "description": "Transcription of reference_audio. Auto-transcribed if omitted.",
            },
            "instruct": {
                "type": "string",
                "description": "Voice design attributes, e.g. 'female, low pitch, british accent'.",
            },
            "device": {
                "type": "string",
                "enum": ["mps", "cpu"],
                "default": "cpu",
                "description": "Inference device. MPS may hang on some models; CPU is stable.",
            },
            "num_step": {
                "type": "integer",
                "default": 32,
                "description": "Diffusion steps (16 for faster inference).",
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "description": "Speed factor (>1.0 faster, <1.0 slower).",
            },
            "output_path": {
                "type": "string",
                "description": "Output WAV path.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=4096, vram_mb=0, disk_mb=1000, network_required=False
    )

    idempotency_key_fields = ["text", "language", "reference_audio", "instruct"]
    side_effects = ["writes WAV to output_path"]
    user_visible_verification = [
        "Listen for natural voice cloning fidelity",
        "Verify pronunciation matches target language",
    ]

    _model = None
    _model_device = None

    def get_status(self) -> ToolStatus:
        try:
            import omnivoice  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def _load_model(self, device: str):
        import torch
        from omnivoice import OmniVoice

        if self._model is not None and self._model_device == device:
            return self._model

        dtype = torch.float16 if device == "mps" else torch.float32
        self._model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice", device_map=device, dtype=dtype
        )
        self._model_device = device
        return self._model

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text required")

        device = inputs.get("device", "cpu")
        out = Path(inputs.get("output_path", "omnivoice_tts.wav"))
        out.parent.mkdir(parents=True, exist_ok=True)

        try:
            import soundfile as sf
            model = self._load_model(device)

            gen_kwargs: dict[str, Any] = {
                "text": text,
                "num_step": inputs.get("num_step", 32),
                "speed": inputs.get("speed", 1.0),
            }
            if inputs.get("language"):
                gen_kwargs["language"] = inputs["language"]
            if inputs.get("reference_audio"):
                gen_kwargs["ref_audio"] = inputs["reference_audio"]
                if inputs.get("ref_text"):
                    gen_kwargs["ref_text"] = inputs["ref_text"]
            if inputs.get("instruct"):
                gen_kwargs["instruct"] = inputs["instruct"]

            audio = model.generate(**gen_kwargs)
            sf.write(str(out), audio[0], 24000)

            duration = len(audio[0]) / 24000.0
            return ToolResult(
                success=True,
                data={
                    "provider": "omnivoice",
                    "language": inputs.get("language"),
                    "output": str(out),
                    "duration_seconds": round(duration, 2),
                    "elapsed_seconds": round(time.time() - start, 2),
                },
                artifacts=[str(out)],
            )
        except Exception as e:
            return ToolResult(success=False, error=f"OmniVoice failed: {e}")
