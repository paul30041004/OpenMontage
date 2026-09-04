"""Google Nano Banana (Gemini image) generation via the generateContent endpoint.

Nano Banana image models (e.g. gemini-2.5-flash-image, gemini-3.1-flash-image)
are served through the Gemini generateContent REST endpoint, not the Imagen
`:predict` endpoint. This tool wraps that path.
"""

from __future__ import annotations

import base64
import os
import time
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
from tools.google_credentials import has_google_credentials

ASPECT_RATIOS = {
    "1:1": (1024, 1024),
    "3:4": (896, 1152),
    "4:3": (1152, 896),
    "9:16": (768, 1344),
    "16:9": (1344, 768),
}

MODELS = [
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-3-pro-image",
    "nano-banana-pro-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-lite-image",
]


def _dims_to_aspect_ratio(width: int, height: int) -> str:
    target = width / height
    best = "1:1"
    best_diff = float("inf")
    for ratio, (w, h) in ASPECT_RATIOS.items():
        diff = abs(target - w / h)
        if diff < best_diff:
            best_diff = diff
            best = ratio
    return best


class GoogleNanoBanana(BaseTool):
    name = "google_nano_banana"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "image_generation"
    provider = "google_nano_banana"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = []
    install_instructions = (
        "Set GOOGLE_API_KEY (or GEMINI_API_KEY) — get one at "
        "https://aistudio.google.com/apikey"
    )
    agent_skills = []

    capabilities = ["generate_image", "generate_illustration", "text_to_image"]
    supports = {
        "negative_prompt": False,
        "seed": True,
        "custom_size": False,
        "aspect_ratio": True,
    }
    best_for = [
        "Nano Banana (Gemini) image generation",
        "editorial/lithograph illustration with strong prompt adherence",
        "stylized and illustrated images via natural-language style",
    ]
    not_good_for = [
        "photoreal-only pipelines (Imagen is stronger there)",
        "offline generation",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {"type": "string", "description": "Image description"},
            "aspect_ratio": {
                "type": "string",
                "enum": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                "default": "1:1",
            },
            "width": {"type": "integer"},
            "height": {"type": "integer"},
            "model": {
                "type": "string",
                "enum": MODELS,
                "default": "gemini-3.1-flash-image",
                "description": "Nano Banana model variant",
            },
            "number_of_images": {
                "type": "integer",
                "default": 1,
                "minimum": 1,
                "maximum": 4,
            },
            "output_path": {"type": "string"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=100, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])
    idempotency_key_fields = ["prompt", "aspect_ratio", "model"]
    side_effects = [
        "writes image file(s) to output_path",
        "calls Google Generative AI generateContent API",
    ]
    user_visible_verification = ["Inspect generated image for relevance and quality"]

    @staticmethod
    def _get_api_key() -> str | None:
        return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

    def get_status(self) -> ToolStatus:
        if has_google_credentials():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        n = inputs.get("number_of_images", 1)
        model = inputs.get("model", "gemini-3.1-flash-image")
        if "pro" in model:
            return 0.06 * n
        return 0.04 * n

    @staticmethod
    def _output_paths(output_path: str | None, count: int) -> list[Path]:
        ext = ".png"
        if not output_path:
            return [Path(f"nano_banana_{idx + 1}{ext}") for idx in range(count)]
        path = Path(output_path)
        suffix = path.suffix or ext
        if count == 1:
            return [path if path.suffix else path.with_suffix(suffix)]
        base = path.with_suffix("") if path.suffix else path
        return [base.parent / f"{base.name}_{idx + 1}{suffix}" for idx in range(count)]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = self._get_api_key()
        if not api_key:
            return ToolResult(
                success=False,
                error="No Google API key found. " + self.install_instructions,
            )

        import requests

        start = time.time()
        model = inputs.get("model", "gemini-3.1-flash-image")
        prompt = inputs["prompt"]

        if "aspect_ratio" in inputs:
            aspect_ratio = inputs["aspect_ratio"]
        elif "width" in inputs and "height" in inputs:
            aspect_ratio = _dims_to_aspect_ratio(inputs["width"], inputs["height"])
        else:
            aspect_ratio = "1:1"

        number_of_images = inputs.get("number_of_images", 1)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "imageConfig": {"aspectRatio": aspect_ratio},
                "candidateCount": number_of_images,
            },
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=120)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            images: list[bytes] = []
            for candidate in candidates:
                parts = (candidate.get("content") or {}).get("parts", [])
                for part in parts:
                    inline = part.get("inlineData") or {}
                    if inline.get("mimeType", "").startswith("image"):
                        images.append(base64.b64decode(inline["data"]))
            if not images:
                return ToolResult(
                    success=False, error="No image data returned from Nano Banana API"
                )

            output_paths = self._output_paths(
                inputs.get("output_path"), len(images)
            )
            outputs: list[str] = []
            for image_bytes, out_path in zip(images, output_paths):
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(image_bytes)
                outputs.append(str(out_path))

        except Exception as e:
            return ToolResult(success=False, error=f"Nano Banana generation failed: {e}")

        return ToolResult(
            success=True,
            data={
                "provider": "google_nano_banana",
                "model": model,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "output": outputs[0],
                "outputs": outputs,
                "images_generated": len(outputs),
            },
            artifacts=outputs,
            cost_usd=self.estimate_cost(inputs),
            duration_seconds=round(time.time() - start, 2),
            model=model,
        )


if __name__ == "__main__":
    import sys

    model = sys.argv[1] if len(sys.argv) > 1 else "gemini-3.1-flash-image"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/nb.png"
    prompt = sys.argv[3] if len(sys.argv) > 3 else "a small red circle on cream paper"
    res = GoogleNanoBanana().execute(
        {"prompt": prompt, "model": model, "output_path": out}
    )
    print(res.success, res.data if res.success else res.error)
