"""OBS Studio WebSocket Remote Controller for OpenMontage.

Controls OBS Studio (v28+ native obs-websocket protocol on port 4455)
for automated live streaming, scene switching, lyrics/camera overlay toggling,
and synchronized broadcast recording.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple

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


class OBSController(BaseTool):
    name = "obs_controller"
    version = "0.1.0"
    tier = ToolTier.PUBLISH
    capability = "video_post"
    provider = "obs"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = []
    install_instructions = (
        "Enable WebSocket Server in OBS Studio:\n"
        "  OBS Studio -> Tools -> WebSocket Server Settings -> Enable (Port 4455)."
    )
    agent_skills = ["ffmpeg"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "start_record", "stop_record",
                    "start_stream", "stop_stream",
                    "set_scene", "get_scenes",
                    "get_status"
                ],
                "description": "OBS Studio action to execute."
            },
            "scene_name": {
                "type": "string",
                "description": "Scene name for 'set_scene'."
            },
            "host": {
                "type": "string",
                "default": "localhost",
                "description": "OBS WebSocket host IP."
            },
            "port": {
                "type": "integer",
                "default": 4455,
                "description": "OBS WebSocket port (default: 4455)."
            },
            "password": {
                "type": "string",
                "default": "",
                "description": "OBS WebSocket authentication password if configured."
            }
        }
    }

    def _execute_obs_request(
        self,
        host: str,
        port: int,
        password: str,
        request_type: str,
        request_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Any]:
        """Connects via WebSocket, handles auth handshake, and sends OBS request."""
        ws_url = f"ws://{host}:{port}"
        try:
            from websockets.sync.client import connect
            with connect(ws_url, open_timeout=2.0) as ws:
                # Step 1: Receive Hello (op 0)
                hello_raw = ws.recv()
                hello = json.loads(hello_raw)
                d = hello.get("d", {})
                auth_info = d.get("authentication")

                # Step 2: Identify with auth if required (op 1)
                identify_data: Dict[str, Any] = {"rpcVersion": 1}
                if auth_info and password:
                    salt = auth_info.get("salt")
                    challenge = auth_info.get("challenge")
                    secret = base64.b64encode(hashlib.sha256((password + salt).encode("utf-8")).digest()).decode("utf-8")
                    auth_resp = base64.b64encode(hashlib.sha256((secret + challenge).encode("utf-8")).digest()).decode("utf-8")
                    identify_data["authentication"] = auth_resp

                ws.send(json.dumps({"op": 1, "d": identify_data}))
                identified_raw = ws.recv()

                # Step 3: Send actual Request (op 6)
                req_msg = {
                    "op": 6,
                    "d": {
                        "requestType": request_type,
                        "requestId": f"om_{int(time.time()*1000)}",
                        "requestData": request_data or {}
                    }
                }
                ws.send(json.dumps(req_msg))
                resp_raw = ws.recv()
                resp = json.loads(resp_raw)

                res_d = resp.get("d", {})
                req_status = res_d.get("requestStatus", {})
                success = req_status.get("result", False)
                return success, res_d.get("responseData", {})
        except Exception as e:
            return False, str(e)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        action = params.get("action", "get_status")
        host = params.get("host", "localhost")
        port = int(params.get("port", 4455))
        password = params.get("password", "")

        req_map = {
            "start_record": "StartRecord",
            "stop_record": "StopRecord",
            "start_stream": "StartStream",
            "stop_stream": "StopStream",
            "get_scenes": "GetSceneList",
            "get_status": "GetRecordStatus",
            "set_scene": "SetCurrentProgramScene"
        }

        req_type = req_map.get(action)
        if not req_type:
            return ToolResult(success=False, error=f"지원하지 않는 액션: {action}")

        req_data = {}
        if action == "set_scene":
            scene = params.get("scene_name")
            if not scene:
                return ToolResult(success=False, error="scene_name이 필요합니다.")
            req_data["sceneName"] = scene

        ok, data = self._execute_obs_request(host, port, password, req_type, req_data)
        if not ok:
            return ToolResult(
                success=False,
                error=f"OBS Studio({host}:{port}) 요청 실패: {data}\n{self.install_instructions}"
            )

        return ToolResult(
            success=True,
            data={
                "action": action,
                "response": data
            }
        )
