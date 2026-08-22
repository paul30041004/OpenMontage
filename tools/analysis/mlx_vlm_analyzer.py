"""Apple Silicon MLX Vision-Language Model analyzer.

Runs local open-source multimodal models (Qwen2-VL, Pixtral, SmolVLM, LLaVA)
natively on Apple Silicon via MLX for zero-cost, private visual QA, scene
analysis, B-roll tagging, and frame understanding.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, List, Optional

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


class MLXVLMAnalyzer(BaseTool):
    name = "mlx_vlm"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "apple_mlx"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:mlx", "python:mlx_vlm"]
    install_instructions = (
        "pip install mlx mlx-vlm\n"
        "Requires: macOS with Apple Silicon (M1/M2/M3/M4)"
    )
    agent_skills = ["video-understand", "video-toolkit"]

    capabilities = [
        "image_understanding",
        "video_frame_qa",
        "visual_description",
        "shot_tagging",
        "apple_silicon_metal",
    ]

    supports = {
        "apple_silicon_native": True,
        "metal_acceleration": True,
        "unified_memory": True,
        "offline": True,
    }

    best_for = [
        "Analyzing and tagging downloaded B-roll footage locally on Mac",
        "Visual quality assurance and text readability check on rendered frames",
        "Generating detailed descriptive prompts from reference images",
    ]

    input_schema = {
        "type": "object",
        "required": ["image_path"],
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to image file or extracted video frame (.jpg, .png).",
            },
            "prompt": {
                "type": "string",
                "default": "Describe this image in detail, including subjects, lighting, colors, camera angle, and mood.",
                "description": "Question or instruction for the vision model.",
            },
            "model_path": {
                "type": "string",
                "default": "mlx-community/Qwen2-VL-7B-Instruct-4bit",
                "description": (
                    "MLX VLM model repository. Options: "
                    "mlx-community/Qwen2-VL-2B-Instruct-4bit (ultra-lightweight), "
                    "mlx-community/Qwen2-VL-7B-Instruct-4bit (high-quality, default), "
                    "mlx-community/SmolVLM-Instruct-4bit"
                ),
            },
            "max_tokens": {
                "type": "integer",
                "default": 300,
                "description": "Maximum generated tokens.",
            },
            "temperature": {
                "type": "number",
                "default": 0.2,
                "description": "Sampling temperature (lower = more factual/deterministic).",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=4000, network_required=False
    )

    idempotency_key_fields = ["image_path", "prompt", "model_path"]
    user_visible_verification = [
        "Verify vision response accurately identifies scene subjects and aesthetics",
    ]

    def get_status(self) -> ToolStatus:
        import platform

        if platform.system() != "Darwin" or platform.machine() != "arm64":
            return ToolStatus.UNAVAILABLE
        try:
            import mlx_vlm  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        image_path = Path(inputs["image_path"])
        if not image_path.exists():
            return ToolResult(
                success=False, error=f"Image file not found: {image_path}"
            )

        prompt = inputs.get(
            "prompt",
            "Describe this image in detail, including subjects, lighting, colors, camera angle, and mood.",
        )
        model_path = inputs.get(
            "model_path", "mlx-community/Qwen2-VL-7B-Instruct-4bit"
        )
        max_tokens = inputs.get("max_tokens", 300)
        temperature = inputs.get("temperature", 0.2)

        try:
            from mlx_vlm import generate, load
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config

            t0 = time.time()
            model, processor = load(model_path)
            config = load_config(model_path)

            formatted_prompt = apply_chat_template(
                processor, config, prompt, num_images=1
            )
            output = generate(
                model,
                processor,
                formatted_prompt,
                [str(image_path)],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            elapsed = time.time() - t0

            return ToolResult(
                success=True,
                data={
                    "provider": "apple_mlx",
                    "model": model_path,
                    "image_path": str(image_path),
                    "prompt": prompt,
                    "response": output.strip(),
                    "elapsed_seconds": round(elapsed, 2),
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"MLX VLM execution failed: {exc}",
            )
