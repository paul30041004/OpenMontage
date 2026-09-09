"""RVC v2 (Retrieval-based Voice Conversion) tool for OpenMontage.

Performs zero-latency neural voice conversion on singing vocals or spoken narration.
Transfers the timbre of a target singer or speaker (.pth + .index) onto any source
audio track while preserving exact pitch, rhythm, dynamics, and breath.
"""

from __future__ import annotations

import os
import shutil
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


class RVCVoiceConverter(BaseTool):
    name = "rvc_voice_converter"
    version = "0.1.0"
    tier = ToolTier.ENHANCE
    capability = "audio_processing"
    provider = "rvc"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Install RVC inference support:\n"
        "  pip install rvc-python\n"
        "Or place weights under tools/_rvc/models/ (e.g. model.pth, model.index)."
    )
    agent_skills = ["musescore-synthv-freeshow", "tts-sample-unification"]

    input_schema = {
        "type": "object",
        "required": ["input_audio", "output_path", "model_path"],
        "properties": {
            "input_audio": {
                "type": "string",
                "description": "Path to source vocal or speech WAV/MP3."
            },
            "output_path": {
                "type": "string",
                "description": "Destination path for converted audio WAV."
            },
            "model_path": {
                "type": "string",
                "description": "Path to target character RVC weights (.pth)."
            },
            "index_path": {
                "type": "string",
                "description": "Optional path to feature index file (.index) for high fidelity timbre matching."
            },
            "pitch_shift": {
                "type": "integer",
                "default": 0,
                "description": "Semitone pitch shift (+12 for male-to-female, -12 for female-to-male, 0 for singing match)."
            },
            "f0_method": {
                "type": "string",
                "enum": ["rmvpe", "crepe", "pm", "harvest"],
                "default": "rmvpe",
                "description": "Pitch extraction algorithm (RMVPE is highest quality and cleanest)."
            },
            "index_rate": {
                "type": "number",
                "default": 0.75,
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Feature retrieval blend ratio (default: 0.75)."
            }
        }
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=4096, vram_mb=2048, disk_mb=2000)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        input_audio = params.get("input_audio")
        if not input_audio or not os.path.exists(input_audio):
            return ToolResult(success=False, error=f"입력 오디오 파일을 찾을 수 없습니다: {input_audio}")

        model_path = params.get("model_path")
        if not model_path or not os.path.exists(model_path):
            return ToolResult(success=False, error=f"RVC 모델 가중치(.pth)를 찾을 수 없습니다: {model_path}")

        output_path = params.get("output_path")
        if not output_path:
            return ToolResult(success=False, error="출력 경로가 지정되지 않았습니다.")

        index_path = params.get("index_path", "")
        pitch_shift = int(params.get("pitch_shift", 0))
        f0_method = params.get("f0_method", "rmvpe")
        index_rate = float(params.get("index_rate", 0.75))

        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        # 1. Try rvc-python CLI / module
        cmd = [
            sys.executable, "-m", "rvc_python", "infer",
            "--input", input_audio,
            "--output", str(out_file),
            "--model", model_path,
            "--pitch", str(pitch_shift),
            "--method", f0_method,
            "--index_rate", str(index_rate)
        ]
        if index_path and os.path.exists(index_path):
            cmd.extend(["--index", index_path])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if res.returncode == 0 and out_file.exists():
                return ToolResult(
                    success=True,
                    data={
                        "output_path": str(out_file),
                        "model": Path(model_path).name,
                        "pitch_shift": pitch_shift,
                        "f0_method": f0_method,
                        "elapsed_seconds": round(time.time() - start_time, 2)
                    },
                    artifacts=[str(out_file)]
                )
        except Exception:
            pass

        # 2. Local fallback: copy and log instructions if rvc-python is not installed yet
        return ToolResult(
            success=False,
            error=(
                f"RVC v2 추론 모듈을 찾을 수 없습니다.\n"
                f"{self.install_instructions}\n"
                f"설치 후 .pth 파일과 함께 다시 실행하세요."
            )
        )
