"""상황별 anchor 음성 라이브러리 기반 통합 내레이션 생성기.

voice_library/에 미리 생성된 상황별 anchor 샘플(documentary/news/emotional/
hype/educational)을 reference_audio로 클론하여, 롱폼/미드폼 영상 전체에 걸쳐
일관된 음성을 생성한다 (tts-sample-unification).

사용:
  from tools.audio.voice_library_tts import VoiceLibraryTTS
  tts = VoiceLibraryTTS()
  tts.execute({
      "text": "내레이션 텍스트",
      "voice": "documentary",   # voice_library의 key
      "output_path": "assets/audio/seg_01.wav",
  })
"""
from __future__ import annotations

import json
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

ROOT = Path(__file__).resolve().parent.parent.parent
VOICE_LIB = ROOT / "voice_library"
MANIFEST_PATH = VOICE_LIB / "voice_library.json"
MANIFEST_50_PATH = VOICE_LIB / "voice_library_50.json"
MANIFEST_HUMAN_50_PATH = VOICE_LIB / "voice_library_human_50.json"


def _load_manifest() -> dict:
    """모든 매니페스트(기본 5 + 숏폼 75 + 휴먼 50)를 병합해 반환."""
    merged = {"version": "1.0", "voices": {}}
    for path in (MANIFEST_PATH, MANIFEST_50_PATH, MANIFEST_HUMAN_50_PATH):
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("voices"):
                    merged["voices"].update(data["voices"])
            except Exception:
                continue
    return merged


class VoiceLibraryTTS(BaseTool):
    name = "voice_library_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "voice_library"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "voice_library/에 상황별 anchor 샘플이 필요합니다.\n"
        "생성: python tools/audio/build_voice_library.py"
    )
    agent_skills = ["tts-sample-unification", "voxcpm-tts", "text-to-speech"]

    capabilities = [
        "tts_ko_emotional",
        "voice_clone",
        "voice_library",
        "consistent_narration",
    ]

    supports = {
        "voice_cloning": True,
        "voice_library": True,
        "consistent_voice": True,
        "offline": True,
    }

    best_for = [
        "롱폼/미드폼 영상의 일관된 내레이션 생성",
        "상황별(다큐/뉴스/감성/하이프/교육) 음성 선택",
        "anchor 샘플 클론으로 음색 통일",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "내레이션 텍스트 (한국어)."},
            "voice": {
                "type": "string",
                "description": "voice_library의 보이스 key (documentary/news/emotional/hype/educational).",
                "default": "documentary",
            },
            "emotion": {
                "type": "string",
                "description": "이 장면의 감정 (선택). 생략 시 anchor의 emotion 사용.",
            },
            "device": {"type": "string", "enum": ["mps", "cpu"], "default": "mps"},
            "timesteps": {"type": "integer", "default": 8},
            "output_path": {"type": "string", "description": "출력 WAV 경로."},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=5000
    )

    idempotency_key_fields = ["text", "voice", "emotion"]
    side_effects = ["writes WAV to output_path"]
    user_visible_verification = [
        "Listen for voice consistency with the anchor sample",
        "Verify emotional delivery matches the scene",
    ]

    def get_status(self) -> ToolStatus:
        manifest = _load_manifest()
        if not manifest.get("voices"):
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def _load_manifest(self) -> dict:
        return _load_manifest()

    def list_voices(self) -> dict:
        return _load_manifest()
        return self._load_manifest()

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text required")

        voice_key = inputs.get("voice", "documentary")
        manifest = self._load_manifest()
        voice = manifest.get("voices", {}).get(voice_key)
        if not voice:
            return ToolResult(
                success=False,
                error=f"voice '{voice_key}' not in library. Available: {list(manifest.get('voices', {}).keys())}",
            )

        anchor_path = voice.get("sample_path")
        if not anchor_path or not Path(anchor_path).exists():
            return ToolResult(success=False, error=f"anchor sample missing: {anchor_path}")

        out = Path(inputs.get("output_path", f"narration_{voice_key}.wav"))
        out.parent.mkdir(parents=True, exist_ok=True)

        try:
            from tools.tool_registry import registry
            registry.discover()
            voxcpm = registry._tools.get("voxcpm_tts")
            if not voxcpm or voxcpm.get_status().name != "AVAILABLE":
                return ToolResult(success=False, error="VoxCPM2 not available")

            # anchor를 reference_audio로 클론 (음색 통일)
            res = voxcpm.execute({
                "text": text,
                "reference_audio": anchor_path,
                "emotion": inputs.get("emotion") or voice.get("emotion"),
                "device": inputs.get("device", voice.get("device", "mps")),
                "timesteps": inputs.get("timesteps", 8),
                "output_path": str(out),
            })

            if not res.success:
                return res

            return ToolResult(
                success=True,
                data={
                    "provider": "voice_library",
                    "voice": voice_key,
                    "voice_label": voice.get("label"),
                    "anchor": anchor_path,
                    "output": str(out),
                    "duration_seconds": res.data.get("duration_seconds"),
                    "elapsed_seconds": round(time.time() - start, 2),
                },
                artifacts=[str(out)],
            )
        except Exception as e:
            return ToolResult(success=False, error=f"VoiceLibraryTTS failed: {e}")
