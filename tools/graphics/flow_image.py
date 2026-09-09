"""Zero-credit image generation via Google Flow browser automation (CDP)."""

from __future__ import annotations

import base64
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


class FlowImage(BaseTool):
    name = "flow_image"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "google_flow"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
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

    capabilities = ["generate_image", "text_to_image", "free_image_generation"]
    supports = {
        "aspect_ratio": True,
        "reference_image": True,
        "zero_cost": True,
    }
    best_for = [
        "100% free image generation (0 credits) with Google Flow (Nano Banana Pro)",
        "generating consistent image batches using an anchor reference image",
        "zero API key, zero GPU hardware required",
    ]
    not_good_for = [
        "sub-second instant generation (takes ~30-50s per image)",
        "in-image Korean text rendering (always overlay Korean text with Remotion)",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string", "description": "Image description"},
            "look_prompt": {
                "type": "string",
                "description": "Common look/lighting/style sentence prepended to prompt",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["9:16", "16:9", "1:1", "4:3", "3:4"],
                "default": "9:16",
            },
            "reference_image_path": {
                "type": "string",
                "description": "Path to local anchor reference image for look consistency",
            },
            "output_path": {
                "type": "string",
                "description": "Destination file path (PNG/JPEG)",
            },
            "chrome_port": {"type": "integer", "default": 9222},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "network"])
    idempotency_key_fields = ["prompt", "aspect_ratio"]
    side_effects = ["writes image file to output_path", "drives Google Flow tab"]
    user_visible_verification = ["Inspect generated image file"]

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
        return 0.0  # 100% free (0 credits in Google Flow)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        port = inputs.get("chrome_port", 9222)
        if not self._check_chrome_port(port):
            return ToolResult(
                success=False,
                error="Chrome remote debugging port not accessible. " + self.install_instructions,
            )

        start = time.time()
        prompt = inputs["prompt"]
        look = inputs.get("look_prompt", "")
        full_prompt = f"{look}. {prompt}" if look else prompt
        output_path = inputs.get("output_path")
        if not output_path:
            output_path = f"flow_images/img_{int(time.time())}.png"
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        try:
            from ._flow_client import FlowClient

            client = FlowClient(port=port)
            client.ensure_image_mode(aspect_ratio=inputs.get("aspect_ratio", "9:16"))

            ref_path = inputs.get("reference_image_path")
            if ref_path and os.path.exists(ref_path):
                client.attach_ingredient_by_path(ref_path)

            download_url = client.generate_image(full_prompt)
            dest = client.download_asset(download_url, Path(output_path))

            return ToolResult(
                success=True,
                data={
                    "file_path": str(dest),
                    "url": download_url,
                    "prompt": full_prompt,
                    "model": "Nano Banana Pro",
                    "credits": 0,
                    "cost": 0.0,
                    "elapsed_seconds": round(time.time() - start, 2),
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Google Flow image generation error: {e}",
            )
