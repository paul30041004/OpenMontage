"""Zero-credit video generation via Google Flow (Veo 3.1 - Lite [Lower Priority] x4)."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

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


class FlowVideo(BaseTool):
    name = "flow_video"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "google_flow"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.ASYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Launch automation Chrome on port 9222:\n"
        '  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" '
        "--remote-debugging-port=9222 --user-data-dir=\"$HOME/.flow-automation-chrome-profile\" "
        '"https://flow.google.com"\n'
        "Log in once with any Google account."
    )
    agent_skills = ["flow-shorts"]

    capabilities = ["generate_video", "text_to_video", "free_video_generation"]
    supports = {
        "aspect_ratio": True,
        "batch_variants": True,
        "zero_cost": True,
    }
    best_for = [
        "100% free video generation (0 credits) with Google Flow Veo 3.1 - Lite [Lower Priority]",
        "generating 4 video variants in a single pass (x4 batch) at zero cost",
        "generating short 9:16 or 16:9 b-roll clips without API keys",
    ]
    not_good_for = [
        "instant / urgent generation (lower priority queue can take 3-10 minutes per clip)",
        "exact duration > 8s in a single generation",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Video motion description. Keep it concise (e.g. '아주 느린 카메라 이동').",
            },
            "duration": {
                "type": "string",
                "enum": ["4s", "6s", "8s"],
                "default": "8s",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["9:16", "16:9"],
                "default": "9:16",
            },
            "batch": {
                "type": "string",
                "enum": ["x1", "x2", "x3", "x4"],
                "default": "x4",
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory for the generated variant video files",
            },
            "chrome_port": {"type": "integer", "default": 9222},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout", "network"])
    idempotency_key_fields = ["prompt", "aspect_ratio", "duration"]
    side_effects = ["writes video files to output_dir", "drives Google Flow tab"]
    user_visible_verification = ["Inspect generated mp4 video files"]

    def _check_chrome_port(self, port: int = 9222) -> bool:
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json/version")
            with urllib.request.urlopen(req, timeout=2):
                return True
        except Exception:
            return False

    def get_status(self) -> ToolStatus:
        if self._check_chrome_port():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0  # 100% free (0 credits in Google Flow with Veo 3.1 Lite [Lower Priority])

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        port = inputs.get("chrome_port", 9222)
        if not self._check_chrome_port(port):
            return ToolResult(
                success=False,
                error="Chrome remote debugging port not accessible. " + self.install_instructions,
            )

        start = time.time()
        prompt = inputs["prompt"]
        duration = inputs.get("duration", "8s")
        aspect = inputs.get("aspect_ratio", "9:16")
        batch = inputs.get("batch", "x4")
        n_expected = int(batch[1])

        output_dir = inputs.get("output_dir", f"flow_videos/clip_{int(time.time())}")
        os.makedirs(output_dir, exist_ok=True)

        try:
            from tools.graphics._flow_client import FlowClient

            client = FlowClient(port=port)
            client.ensure_video_mode(aspect_ratio=aspect, duration=duration, batch=batch)

            variants_info = client.generate_video(prompt, variants=n_expected)
            downloaded = []
            for i, vinfo in enumerate(variants_info):
                suffix = "" if i == 0 else f"-v{i + 1}"
                dest = Path(output_dir) / f"video{suffix}.mp4"
                client.download_asset(vinfo["url"], dest)
                downloaded.append({
                    "file_path": str(dest),
                    "url": vinfo["url"],
                    "width": vinfo.get("width", 720),
                    "height": vinfo.get("height", 1280),
                    "duration": vinfo.get("duration", 8),
                })

            return ToolResult(
                success=True,
                data={
                    "model": "Veo 3.1 - Lite [Lower Priority]",
                    "prompt": prompt,
                    "duration": duration,
                    "batch": batch,
                    "credits": 0,
                    "cost": 0.0,
                    "variants": downloaded,
                    "primary_file": downloaded[0]["file_path"] if downloaded else None,
                    "elapsed_seconds": round(time.time() - start, 2),
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Google Flow video generation error: {e}",
            )
