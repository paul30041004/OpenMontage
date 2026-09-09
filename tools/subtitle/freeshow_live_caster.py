"""FreeShow WebSocket/HTTP Live Caster for OpenMontage.

Enables real-time remote control and timeline-synchronized slide projection
to FreeShow (open-source worship & presentation software) over WebSocket or HTTP API.
Supports automatic slide advancing synchronized with video/audio playback.
"""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
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


class FreeShowLiveCaster(BaseTool):
    name = "freeshow_live_caster"
    version = "0.1.0"
    tier = ToolTier.PUBLISH
    capability = "subtitle"
    provider = "freeshow"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = []
    install_instructions = (
        "FreeShow should be running with Remote Control enabled in Settings:\n"
        "  FreeShow -> Settings -> Connection -> Enable Remote / Server (Port 5505)."
    )
    agent_skills = ["musescore-synthv-freeshow"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {
                "type": "string",
                "enum": ["next", "previous", "clear", "show_slide", "sync_timeline", "ping"],
                "description": "Action to send to FreeShow remote server."
            },
            "host": {
                "type": "string",
                "default": "127.0.0.1",
                "description": "FreeShow host IP (default: 127.0.0.1 for local, or LAN IP for church network)."
            },
            "port": {
                "type": "integer",
                "default": 5505,
                "description": "FreeShow remote control port (default: 5505)."
            },
            "slide_index": {
                "type": "integer",
                "description": "Target slide index (0-based) for 'show_slide'."
            },
            "subtitles_json": {
                "type": "string",
                "description": "Path to subtitles.json for 'sync_timeline' synchronized playback."
            }
        }
    }

    def _send_command(self, host: str, port: int, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """Sends HTTP or raw TCP JSON command to FreeShow remote server."""
        # Try HTTP endpoint first
        url = f"http://{host}:{port}/api/action"
        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return True, resp.read().decode("utf-8")
        except Exception:
            pass

        # Try raw TCP socket command
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((host, port))
                s.sendall(json.dumps(payload).encode("utf-8") + b"\n")
                return True, "TCP command sent"
        except Exception as e:
            return False, str(e)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        action = params.get("action", "next").lower()
        host = params.get("host", "127.0.0.1")
        port = int(params.get("port", 5505))

        payload: Dict[str, Any] = {"action": action}

        if action == "show_slide":
            idx = params.get("slide_index", 0)
            payload["slide_index"] = idx
            payload["index"] = idx

        elif action == "sync_timeline":
            sub_path = params.get("subtitles_json")
            if not sub_path or not Path(sub_path).exists():
                return ToolResult(success=False, error=f"자막 JSON 파일을 찾을 수 없습니다: {sub_path}")

            with open(sub_path, "r", encoding="utf-8") as f:
                sub_data = json.load(f)

            slides = sub_data.get("slides", [])
            print(f"🎬 FreeShow 타임라인 실시간 송출 시작 (총 {len(slides)}개 슬라이드)...")
            start_time = time.time()

            for i, s in enumerate(slides):
                target_sec = (s.get("time_start_ms", 0) or 0) / 1000.0
                elapsed = time.time() - start_time
                if target_sec > elapsed:
                    time.sleep(target_sec - elapsed)

                lines_text = " / ".join(s.get("lines", []))
                print(f"  [FreeShow Slide {i+1}] ({target_sec:.1f}s): {lines_text}")
                self._send_command(host, port, {"action": "show_slide", "slide_index": i})

            return ToolResult(
                success=True,
                data={
                    "status": "timeline_completed",
                    "slides_cast": len(slides),
                    "total_duration_sec": round(time.time() - start_time, 2)
                }
            )

        # Standard command execution
        ok, resp_str = self._send_command(host, port, payload)
        return ToolResult(
            success=ok,
            data={"action": action, "host": host, "port": port, "response": resp_str},
            error=None if ok else f"FreeShow({host}:{port}) 연결 실패: {resp_str}. FreeShow 원격 제어가 켜져 있는지 확인하세요."
        )
