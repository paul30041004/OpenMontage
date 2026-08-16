"""Fish Audio cloud TTS provider tool."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx

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


class FishAudioTTS(BaseTool):
    name = "fish_audio_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "fish_audio"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["python:httpx"]
    install_instructions = (
        "Set the FISH_API_KEY environment variable:\n"
        "  export FISH_API_KEY=your_key_here\n"
        "Get a key at https://fish.audio/ (API key in account settings).\n"
    )
    fallback = "voxcpm_tts"
    fallback_tools = ["voxcpm_tts", "kokoro_tts"]
    agent_skills = ["fish-audio"]

    capabilities = [
        "text_to_speech",
        "voice_selection",
        "voice_cloning",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": False,
        "native_audio": True,
    }
    best_for = [
        "high-quality cloud narration (Korean and other languages)",
        "production TTS when local voices sound robotic",
        "voice clone via reference_id or raw reference audio",
    ]
    not_good_for = [
        "offline / air-gapped workflows",
        "zero-cost production",
    ]

    input_schema = {
        "type": "object",
        "required": [],
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["tts", "create_voice"],
                "default": "tts",
                "description": "tts: text-to-speech synthesis. create_voice: clone an anchor audio sample into a persistent Fish Audio voice model (returns reference_id for reuse).",
            },
            "text": {"type": "string"},
            "model": {
                "type": "string",
                "default": "s2.1-pro",
                "enum": ["s2.1-pro", "s2.1-pro-free", "s2-pro", "s1"],
                "description": "Fish Audio TTS model. s2-pro is multilingual (incl. Korean); s1 uses (parenthesis) emotion tags.",
            },
            "voice": {
                "type": "string",
                "description": "Fish Audio voice reference_id from the Voice Library (e.g. a Korean narrator voice). Optional — omit for default voice.",
            },
            "reference_id": {
                "type": "string",
                "description": "Alias for voice. Passed as the reference_id to POST /v1/tts.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to a local voice sample (WAV/MP3/M4A/OPUS). For operation=create_voice it is the cloning source. For operation=tts it triggers an instant (inline) clone via the `references` request body.",
            },
            "reference_audio_text": {
                "type": "string",
                "description": "Transcript of reference_audio (sharpens instant-clone pronunciation). For create_voice, optionally the sample's transcript.",
            },
            "voice_title": {
                "type": "string",
                "description": "Title for a created voice model (operation=create_voice). Defaults to project/sample-derived name.",
            },
            "format": {
                "type": "string",
                "default": "mp3",
                "enum": ["mp3", "wav", "pcm", "opus"],
                "description": "Output audio format.",
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "minimum": 0.5,
                "maximum": 2.0,
                "description": "Speech speed (0.5–2.0). Maps to prosody.speed.",
            },
            "sample_rate": {
                "type": "integer",
                "description": "Sample rate when format=wav (e.g. 44100).",
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["text", "voice", "reference_id", "model", "format", "speed"]
    side_effects = ["writes audio file to output_path", "calls Fish Audio API"]
    user_visible_verification = ["Listen to generated audio for intelligibility and tone"]

    BASE_URL = "https://api.fish.audio"

    def get_status(self) -> ToolStatus:
        if os.environ.get("FISH_API_KEY"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        # ~$0.003 per 1k chars on s2-pro family; approximate.
        # create_voice has no text; cost it at the free tier (0).
        return round(len(inputs.get("text", "") or "") * 0.000003, 4)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        key = os.environ.get("FISH_API_KEY")
        if not key:
            return ToolResult(
                success=False,
                error="No Fish Audio API key. " + self.install_instructions,
            )

        start = time.time()
        try:
            operation = inputs.get("operation", "tts")
            if operation == "create_voice":
                result = self._create_voice(api_key, inputs)
            else:
                result = self._generate(api_key, inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"Fish Audio TTS failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        result.cost_usd = self.estimate_cost(inputs)
        return result

    def _create_voice(self, api_key: str, inputs: dict[str, Any]) -> ToolResult:
        """Clone a local anchor sample into a persistent Fish Audio voice model."""
        ref_audio = inputs.get("reference_audio")
        if not ref_audio:
            return ToolResult(
                success=False,
                error="create_voice requires reference_audio (path to a voice sample WAV/MP3).",
            )
        sample = Path(ref_audio)
        if not sample.is_file():
            return ToolResult(success=False, error=f"reference_audio not found: {sample}")

        title = inputs.get("voice_title") or f"cloned-{time.strftime('%Y%m%d-%H%M%S')}"

        with open(sample, "rb") as f:
            files = {
                "type": (None, "tts"),
                "title": (None, title),
                "visibility": (None, "private"),
                "train_mode": (None, "fast"),
                "voices": (sample.name, f.read(), "audio/wav"),
            }
            headers = {"Authorization": f"Bearer {api_key}"}
            if inputs.get("reference_audio_text"):
                files["texts"] = (None, inputs["reference_audio_text"])

            resp = httpx.post(
                f"{self.BASE_URL}/model",
                headers=headers,
                files=files,
                timeout=180.0,
            )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Fish Audio create_voice returned {resp.status_code}: {resp.text[:400]}"
            )

        data = resp.json()
        voice_id = data.get("_id") or data.get("id") or data.get("model_id")
        state = data.get("state") or "created"
        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "operation": "create_voice",
                "voice_title": title,
                "reference_id": voice_id,
                "state": state,
                "message": (
                    "Voice model created. Pass reference_id to every subsequent "
                    "tts call for a consistent cloned voice across all narration segments."
                ),
            },
            model=self.provider,
        )

    def _generate(self, api_key: str, inputs: dict[str, Any]) -> ToolResult:
        from tools.analysis.audio_probe import probe_duration

        text = inputs["text"]
        model = inputs.get("model", "s2.1-pro")
        voice = inputs.get("voice") or inputs.get("reference_id")
        fmt = inputs.get("format", "mp3")
        speed = float(inputs.get("speed", 1.0))
        sample_rate = inputs.get("sample_rate")

        output_path = Path(inputs.get("output_path", f"fish_audio_tts.{fmt}"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload: dict[str, Any] = {"text": text, "format": fmt}
        if voice:
            payload["reference_id"] = voice
        elif inputs.get("reference_audio"):
            # Instant clone is possible but requires a MessagePack body (raw binary in
            # the `references` array), which the JSON path here can't carry efficiently.
            # For one-voice-many-segments (mid-form/multi-section narration), use
            # operation='create_voice' once to get a persistent reference_id, then send
            # that reference_id on every tts call. Returning a clear error guides that.
            return ToolResult(
                success=False,
                error=(
                    "Instant clone needs a MessagePack request body, not supported via "
                    "this JSON path. Use operation='create_voice' with reference_audio "
                    "to make a persistent voice model, then pass its reference_id to "
                    "each tts call for a consistent voice across all segments."
                ),
            )
        if speed != 1.0:
            payload["prosody"] = {"speed": speed}
        if sample_rate:
            payload["sample_rate"] = sample_rate

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "model": model,
        }

        resp = httpx.post(
            f"{self.BASE_URL}/v1/tts",
            headers=headers,
            json=payload,
            timeout=120.0,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Fish Audio API returned {resp.status_code}: {resp.text[:400]}"
            )

        output_path.write_bytes(resp.content)
        if output_path.stat().st_size < 1000:
            raise RuntimeError("Fish Audio produced a near-empty audio file")

        audio_duration = probe_duration(output_path)

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": model,
                "voice": voice or "default",
                "format": fmt,
                "speed": speed,
                "text_length": len(text),
                "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
                "output": str(output_path),
            },
            artifacts=[str(output_path)],
            model=model,
        )
