"""Kokoro-82M local text-to-speech provider tool (pykokoro, ONNX CPU)."""

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


class KokoroTTS(BaseTool):
    name = "kokoro_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "kokoro"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:pykokoro"]
    install_instructions = (
        "Install Kokoro TTS:\n"
        "  pip install 'pykokoro[cpu]'\n"
        "First run downloads the Kokoro-82M ONNX model (~300MB) from HuggingFace "
        "into ~/.cache/pykokoro."
    )
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "offline_generation",
    ]
    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "high-quality offline narration",
        "privacy-sensitive local-only workflows",
        "multi-language voiceover (en, es, fr, de, it, pt, ja, zh, ko)",
    ]
    not_good_for = [
        "voice clone matching",
        "very long single-pass documents (stream per paragraph instead)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "voice": {
                "type": "string",
                "default": "af_sarah",
                "description": "Kokoro voice id, e.g. af_sarah, am_michael, bf_emma, bm_george, jf_alpha, zf_xiaobei",
            },
            "lang": {
                "type": "string",
                "default": "en-us",
                "description": "Language code for phonemization (en-us, en-gb, es, fr, de, it, pt, ja, zh, ko)",
            },
            "speed": {
                "type": "number",
                "default": 1.0,
            },
            "model_quality": {
                "type": "string",
                "enum": ["fp32", "fp16", "q8", "q4"],
                "default": "fp16",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=500, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["text", "voice", "lang", "speed", "model_quality"]
    side_effects = ["writes audio file to output_path", "downloads model to ~/.cache/pykokoro on first run"]
    user_visible_verification = ["Listen to generated audio for intelligibility"]

    _pipeline = None

    def get_status(self) -> ToolStatus:
        try:
            import pykokoro  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        try:
            import pykokoro  # noqa: F401
        except ImportError as exc:
            raise DependencyError(
                f"Python module 'pykokoro' not installed. {self.install_instructions}"
            ) from exc

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def _get_pipeline(self):
        if self._pipeline is None:
            from pykokoro import KokoroPipeline, PipelineConfig
            from pykokoro.generation_config import GenerationConfig

            config = PipelineConfig(
                voice="af_sarah",
                provider="cpu",
                model_quality="fp16",
                generation=GenerationConfig(lang="en-us", speed=1.0),
            )
            self._pipeline = KokoroPipeline(config)
        return self._pipeline

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(
                success=False,
                error="Kokoro TTS not available. " + self.install_instructions,
            )

        start = time.time()
        try:
            result = self._generate(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"Kokoro TTS generation failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _generate(self, inputs: dict[str, Any]) -> ToolResult:
        from pykokoro import KokoroPipeline, PipelineConfig
        from pykokoro.generation_config import GenerationConfig

        output_path = Path(inputs.get("output_path", "tts_output.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voice = inputs.get("voice", "af_sarah")
        lang = inputs.get("lang", "en-us")
        speed = float(inputs.get("speed", 1.0))
        quality = inputs.get("model_quality", "fp16")

        config = PipelineConfig(
            voice=voice,
            provider="cpu",
            model_quality=quality,
            generation=GenerationConfig(lang=lang, speed=speed),
        )
        pipeline = KokoroPipeline(config)
        try:
            res = pipeline.run(inputs["text"])
            res.save_wav(str(output_path))
        finally:
            pipeline.close()

        if not output_path.exists():
            return ToolResult(success=False, error=f"Kokoro output file missing: {output_path}")

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": "Kokoro-82M",
                "voice": voice,
                "lang": lang,
                "speed": speed,
                "text_length": len(inputs["text"]),
                "output": str(output_path),
                "format": "wav",
            },
            artifacts=[str(output_path)],
            model="Kokoro-82M",
        )
