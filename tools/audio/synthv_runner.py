"""Synthesizer V Studio Pro integration tool for OpenMontage.

Manages Synthesizer V Pro project (.svp) render configurations, auto-assigns
output directories, and automates export of high-resolution vocal audio stems.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class SynthVRunner(BaseTool):
    name = "synthv_runner"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "vocal_synthesis"
    provider = "dreamtonics"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["app:Synthesizer V Studio"]
    install_instructions = (
        "Dreamtonics Synthesizer V Studio Pro is required on macOS:\n"
        "Download and install Synthesizer V Studio 2 Pro or Synthesizer V Studio Pro."
    )
    agent_skills = ["musescore-synthv-freeshow"]

    input_schema = {
        "type": "object",
        "required": ["svp_path"],
        "properties": {
            "svp_path": {
                "type": "string",
                "description": "Path to the .svp Synthesizer V project file."
            },
            "output_dir": {
                "type": "string",
                "description": "Destination directory for rendered vocal WAV files."
            },
            "open_editor": {
                "type": "boolean",
                "default": True,
                "description": "Whether to launch Synthesizer V Studio Pro app with this project."
            },
            "wait_for_render": {
                "type": "boolean",
                "default": False,
                "description": "Whether to wait and poll for the rendered WAV file to appear."
            },
            "timeout_seconds": {
                "type": "integer",
                "default": 120,
                "description": "Maximum seconds to wait if wait_for_render is True."
            }
        }
    }

    def _find_synthv_app(self) -> Optional[str]:
        candidates = [
            "/Applications/Synthesizer V Studio 2 Pro.app",
            "/Applications/Synthesizer V Studio Pro.app",
            "/Applications/Synthesizer V Studio 2 Basic.app",
            "/Applications/Synthesizer V Studio Basic.app"
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        svp_path = params.get("svp_path")
        if not svp_path or not os.path.exists(svp_path):
            return ToolResult(
                success=False,
                error=f".svp 프로젝트 파일을 찾을 수 없습니다: {svp_path}"
            )

        svp_file = Path(svp_path).resolve()
        output_dir = params.get("output_dir")
        if not output_dir:
            output_dir = str(svp_file.parent / "audio")

        os.makedirs(output_dir, exist_ok=True)
        out_dir_path = Path(output_dir).resolve()

        # Update .svp renderConfig with target destination
        try:
            with open(svp_file, "r", encoding="utf-8") as f:
                svp_data = json.load(f)

            if "renderConfig" not in svp_data:
                svp_data["renderConfig"] = {}

            base_name = svp_file.stem
            svp_data["renderConfig"]["destination"] = str(out_dir_path)
            svp_data["renderConfig"]["filename"] = base_name
            svp_data["renderConfig"]["numChannels"] = 2
            svp_data["renderConfig"]["bitDepth"] = 24
            svp_data["renderConfig"]["sampleRate"] = 48000

            with open(svp_file, "w", encoding="utf-8") as f:
                json.dump(svp_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            return ToolResult(
                success=False,
                error=f".svp 렌더 설정 주입 실패: {e}"
            )

        tracks = svp_data.get("tracks", [])
        expected_wavs = []
        for t in tracks:
            t_name = t.get("name", "vocal")
            expected_wavs.append(str(out_dir_path / f"{base_name}_{t_name}.wav"))
            expected_wavs.append(str(out_dir_path / f"{t_name}.wav"))
            expected_wavs.append(str(out_dir_path / f"{base_name}.wav"))

        app_path = self._find_synthv_app()
        open_editor = params.get("open_editor", True)
        launched = False

        if open_editor:
            if app_path:
                try:
                    subprocess.run(["open", "-a", app_path, str(svp_file)], check=True)
                    launched = True
                except Exception as e:
                    print(f"Synthesizer V 실행 경고: {e}")
            else:
                try:
                    subprocess.run(["open", str(svp_file)], check=True)
                    launched = True
                except Exception:
                    pass

        wait_for_render = params.get("wait_for_render", False)
        timeout = params.get("timeout_seconds", 120)
        found_wav: Optional[str] = None

        if wait_for_render:
            start_t = time.time()
            while time.time() - start_t < timeout:
                for candidate in expected_wavs:
                    if os.path.exists(candidate) and os.path.getsize(candidate) > 1000:
                        found_wav = candidate
                        break
                # Also check any new WAV in output_dir
                if not found_wav:
                    wav_files = list(out_dir_path.glob("*.wav"))
                    if wav_files:
                        found_wav = str(wav_files[0])
                        break
                time.sleep(1.0)

        return ToolResult(
            success=True,
            data={
                "svp_path": str(svp_file),
                "output_dir": str(out_dir_path),
                "app_detected": app_path,
                "launched": launched,
                "track_count": len(tracks),
                "rendered_wav": found_wav,
                "instructions": (
                    f"Synthesizer V Studio Pro에서 {svp_file.name} 프로젝트가 열렸습니다. "
                    f"'File' > 'Export to Audio Files' (또는 Cmd+R)를 누르면 "
                    f"'{out_dir_path}'에 24-bit 48kHz 고음질 보컬 트랙이 추출됩니다."
                )
            }
        )
