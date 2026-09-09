"""VoiceStudio (OmniVoice-Studio) local text-to-speech adapter tool for OpenMontage.

Connects to a running VoiceStudio instance (http://localhost:3900) via its
standard OpenAI-compatible audio API (/v1/audio/speech).

Provides local zero-shot voice cloning, voice design, and speech synthesis
across 16 TTS engines (OmniVoice, CosyVoice 3, VoxCPM2, IndexTTS, PocketTTS, etc.)
and 646 languages without dependency conflicts.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
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

DEFAULT_BASE_URL = "http://localhost:3900/v1"
DISCOVERY_URL = "http://localhost:3900/.well-known/voicestudio-speech"
VOICES_URL = "http://localhost:3900/v1/audio/voices"


class VoiceStudioTTS(BaseTool):
    name = "voicestudio_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "voicestudio"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["service:voicestudio"]
    install_instructions = (
        "VoiceStudio runs as a local background service on localhost:3900.\n"
        "1. Download & launch the macOS app: https://github.com/debpalash/VoiceStudio/releases/latest\n"
        "2. Or run via Docker:\n"
        "   docker run -d -p 127.0.0.1:3900:3900 -v omnivoice-data:/app/omnivoice_data palashdeb/omnivoice-studio:stable"
    )
    agent_skills = ["voicestudio", "text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "voice_design",
        "multilingual_tts"
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
    }
    best_for = [
        "646-language local zero-shot voice cloning",
        "local ElevenLabs alternative with OpenAI-compatible API",
        "accessing 16 engines (OmniVoice, CosyVoice, VoxCPM2) without venv conflicts",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize into speech."
            },
            "voice": {
                "type": "string",
                "default": "default",
                "description": "Voice profile ID or preset name saved in VoiceStudio."
            },
            "model": {
                "type": "string",
                "default": "tts-1",
                "description": "Engine or model ID in VoiceStudio (e.g. 'tts-1', 'omnivoice', 'cosyvoice-3', 'voxcpm2')."
            },
            "language": {
                "type": "string",
                "default": "auto",
                "description": "Output language code (e.g. 'ko', 'en', 'ja', 'auto')."
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "minimum": 0.5,
                "maximum": 2.0,
                "description": "Speech speed multiplier."
            },
            "response_format": {
                "type": "string",
                "enum": ["wav", "mp3", "opus", "flac"],
                "default": "wav",
                "description": "Output audio format."
            },
            "output_path": {
                "type": "string",
                "description": "File path to save the generated audio."
            },
            "base_url": {
                "type": "string",
                "default": DEFAULT_BASE_URL,
                "description": "VoiceStudio API base URL (default: http://localhost:3900/v1)."
            }
        }
    }

    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=100)
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["connection_error", "timeout"])

    def get_status(self) -> ToolStatus:
        """Check if VoiceStudio local server is running on localhost:3900."""
        try:
            req = urllib.request.Request(DISCOVERY_URL, headers={"User-Agent": "OpenMontage"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return ToolStatus.AVAILABLE
        except Exception:
            try:
                req = urllib.request.Request(VOICES_URL, headers={"User-Agent": "OpenMontage"})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        return ToolStatus.AVAILABLE
            except Exception:
                pass
        return ToolStatus.UNAVAILABLE

    def _get_ffprobe(self) -> str:
        for c in ["ffprobe", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffprobe", "/opt/homebrew/bin/ffprobe"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffprobe"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = params.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="합성할 텍스트(text)가 비어있습니다.")

        base_url = params.get("base_url", DEFAULT_BASE_URL).rstrip("/")
        speech_url = f"{base_url}/audio/speech"

        voice = params.get("voice", "default")
        model = params.get("model", "tts-1")
        speed = float(params.get("speed", 1.0))
        resp_format = params.get("response_format", "wav").lower()

        out_path = params.get("output_path")
        if not out_path:
            out_path = f"voicestudio_{int(time.time())}.{resp_format}"

        out_file = Path(out_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "response_format": resp_format
        }

        # Optional language header/property if provided
        lang = params.get("language")
        if lang and lang != "auto":
            payload["language"] = lang

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenMontage/VoiceStudioAdapter"
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(speech_url, data=req_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                with open(out_file, "wb") as f:
                    while chunk := response.read(65536):
                        f.write(chunk)
        except urllib.error.URLError as e:
            return ToolResult(
                success=False,
                error=(
                    f"VoiceStudio 로컬 서버({base_url})에 연결할 수 없습니다: {e}\n"
                    f"VoiceStudio 앱을 실행했거나 localhost:3900 포트가 열려 있는지 확인하세요.\n"
                    f"{self.install_instructions}"
                )
            )
        except Exception as e:
            return ToolResult(success=False, error=f"VoiceStudio 합성 오류: {e}")

        if not out_file.exists() or out_file.stat().st_size < 500:
            return ToolResult(success=False, error="VoiceStudio에서 오디오 파일이 정상적으로 생성되지 않았습니다.")

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
                "provider": "voicestudio",
                "model": model,
                "voice": voice,
                "output_path": str(out_file),
                "duration_seconds": round(duration_sec, 2),
                "file_size": out_file.stat().st_size,
                "format": resp_format,
                "inference_time": round(time.time() - start_time, 2)
            },
            artifacts=[str(out_file)]
        )
