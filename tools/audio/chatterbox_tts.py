"""Chatterbox TTS — SoTA open-source voice cloning (Resemble AI, MIT).

Instant voice cloning from a short reference clip. This is the model behind
the viral AI voice-clone videos on X/Threads: speak in one voice, clone it
from 5-20 seconds of audio, and synthesize new narration in that voice.

Runs fully locally on CPU / Apple Silicon MPS.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    DependencyError,
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


class ChatterboxTTS(BaseTool):
    name = "chatterbox_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "chatterbox"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:chatterbox"]
    install_instructions = (
        "Install Chatterbox TTS:\n"
        "  pip install chatterbox-tts\n"
        "First run downloads the model (~2GB) from HuggingFace into the HF cache."
    )
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "offline_generation",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "instant voice cloning from a short reference clip",
        "viral AI voice-clone narration",
        "character / creator voiceover",
    ]
    not_good_for = [
        "single-digit-second latency realtime synthesis",
        "singing voice conversion",
    ]

    input_schema = {
        "type": "object",
        "required": ["text", "reference_audio"],
        "properties": {
            "text": {"type": "string"},
            "reference_audio": {
                "type": "string",
                "description": "Path to a 5-30s reference clip of the voice to clone",
            },
            "exaggeration": {
                "type": "number",
                "default": 0.5,
                "description": "Emotion intensity of the clone (0.0 flat .. 1.0 expressive)",
            },
            "temperature": {
                "type": "number",
                "default": 0.8,
            },
            "cfg_weight": {
                "type": "number",
                "default": 0.5,
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=4096, vram_mb=0, disk_mb=2500, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["text", "reference_audio", "exaggeration", "temperature"]
    side_effects = [
        "writes audio file to output_path",
        "downloads model to HF cache on first run",
    ]
    user_visible_verification = [
        "Compare the output voice against the reference clip",
    ]

    _model = None

    def get_status(self) -> ToolStatus:
        try:
            import chatterbox  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        try:
            import chatterbox  # noqa: F401
        except ImportError as exc:
            raise DependencyError(
                f"Python module 'chatterbox' not installed. {self.install_instructions}"
            ) from exc

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def _get_model(self):
        if self._model is None:
            import torch
            from chatterbox import ChatterboxTTS

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            self._model = ChatterboxTTS.from_pretrained(device)
            self._model.device = device
        return self._model

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(
                success=False,
                error="Chatterbox TTS not available. " + self.install_instructions,
            )

        start = time.time()
        try:
            result = self._generate(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"Chatterbox generation failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any]) -> ToolResult:
        import soundfile as sf
        import torch

        output_path = Path(inputs.get("output_path", "tts_output.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        reference = Path(inputs["reference_audio"]).expanduser()
        if not reference.is_file():
            return ToolResult(
                success=False,
                error=f"Reference audio not found: {reference}",
            )

        model = self._get_model()
        wav = model.generate(
            inputs["text"],
            audio_prompt_path=str(reference),
            exaggeration=float(inputs.get("exaggeration", 0.5)),
            temperature=float(inputs.get("temperature", 0.8)),
            cfg_weight=float(inputs.get("cfg_weight", 0.5)),
        )
        wav = wav.squeeze(0).detach().cpu().numpy()
        sf.write(str(output_path), wav, model.sr)

        if not output_path.exists():
            return ToolResult(
                success=False,
                error=f"Chatterbox output file missing: {output_path}",
            )

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": "Chatterbox",
                "reference_audio": str(reference),
                "exaggeration": inputs.get("exaggeration", 0.5),
                "text_length": len(inputs["text"]),
                "output": str(output_path),
                "format": "wav",
                "sample_rate": model.sr,
            },
            artifacts=[str(output_path)],
            model="Chatterbox",
        )
