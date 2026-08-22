"""Apple Silicon MLX Language Model generator.

Runs local open-source LLMs (Qwen 2.5, Llama 3.2, EXAONE 3.5, Mistral)
natively on Apple Silicon via MLX with unified memory and Metal acceleration
for 100% offline, zero-cost, private script writing, research structuring,
and video scene planning.
"""

from __future__ import annotations

import json
import time
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


class MLXLMWriter(BaseTool):
    name = "mlx_lm"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "graphics"
    provider = "apple_mlx"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:mlx", "python:mlx_lm"]
    install_instructions = (
        "pip install mlx mlx-lm\n"
        "Requires: macOS with Apple Silicon (M1/M2/M3/M4)"
    )
    agent_skills = ["storytelling", "video-toolkit"]

    capabilities = [
        "script_generation",
        "scene_planning",
        "research_synthesis",
        "prompt_refinement",
        "apple_silicon_metal",
    ]

    supports = {
        "apple_silicon_native": True,
        "metal_acceleration": True,
        "unified_memory": True,
        "offline": True,
    }

    best_for = [
        "Local, offline script drafting and translation on Apple Silicon",
        "Generating scene-by-scene timing and camera direction prompts",
        "Zero-cost brainstorming and Hook formulation without API tokens",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "User prompt or instructions for script writing/planning.",
            },
            "system_prompt": {
                "type": "string",
                "default": "You are a professional documentary and viral video script director. Write concise, punchy, retention-focused content.",
                "description": "System instruction defining agent persona and quality standards.",
            },
            "model_path": {
                "type": "string",
                "default": "mlx-community/Qwen2.5-7B-Instruct-4bit",
                "description": (
                    "MLX LM model repository. Options: "
                    "mlx-community/Qwen2.5-7B-Instruct-4bit (recommended balanced), "
                    "mlx-community/Qwen2.5-3B-Instruct-4bit (fastest), "
                    "mlx-community/Llama-3.2-3B-Instruct-4bit, "
                    "mlx-community/EXAONE-3.5-7.8B-Instruct-4bit (best Korean)"
                ),
            },
            "max_tokens": {
                "type": "integer",
                "default": 1024,
                "description": "Maximum generated tokens.",
            },
            "temperature": {
                "type": "number",
                "default": 0.6,
                "description": "Creativity temperature.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=5000, network_required=False
    )

    idempotency_key_fields = ["prompt", "system_prompt", "model_path"]
    user_visible_verification = [
        "Verify generated script flows logically and meets target timing/tone",
    ]

    def get_status(self) -> ToolStatus:
        import platform

        if platform.system() != "Darwin" or platform.machine() != "arm64":
            return ToolStatus.UNAVAILABLE
        try:
            import mlx_lm  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        prompt = inputs.get("prompt", "").strip()
        if not prompt:
            return ToolResult(success=False, error="Prompt cannot be empty.")

        system_prompt = inputs.get(
            "system_prompt",
            "You are a professional documentary and viral video script director.",
        )
        model_path = inputs.get(
            "model_path", "mlx-community/Qwen2.5-7B-Instruct-4bit"
        )
        max_tokens = inputs.get("max_tokens", 1024)
        temperature = inputs.get("temperature", 0.6)

        try:
            from mlx_lm import generate, load

            t0 = time.time()
            model, tokenizer = load(model_path)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
            formatted_prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            response = generate(
                model,
                tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                temp=temperature,
            )
            elapsed = time.time() - t0

            return ToolResult(
                success=True,
                data={
                    "provider": "apple_mlx",
                    "model": model_path,
                    "response": response.strip(),
                    "elapsed_seconds": round(elapsed, 2),
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"MLX LM execution failed: {exc}",
            )
