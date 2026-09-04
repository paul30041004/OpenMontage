"""Cloud video-gen character consistency tools.

These tools orchestrate the ViMax-style pattern for OpenMontage: define each
character once, generate anchor reference frames, then bind those references
into every downstream video generation call so one character keeps a single,
consistent appearance across many scenes.

The creative orchestration (when to generate anchors, how many views, which
scenes bind which characters) lives in skills and pipeline manifests. Python
only produces the structured `character_consistency` artifact and, optionally,
generates the anchor images via the image-selector layer.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from schemas.artifacts import validate_artifact
from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStatus,
    ToolStability,
    ToolTier,
)


def _write_json(path: str | None, data: dict[str, Any]) -> list[str]:
    if not path:
        return []
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return [str(out)]


def _slug(value: str) -> str:
    chars = [c.lower() if c.isalnum() else "-" for c in value.strip()]
    return "-".join("".join(chars).split("-")).strip("-") or "character"


class CharacterConsistencyBuilder(BaseTool):
    """Build the character_consistency artifact and anchor reference frames.

    Two operations:
    - ``build``: normalize character specs into a schema-valid
      ``character_consistency`` artifact (no image generation).
    - ``generate_frames``: for each character, generate anchor reference
      frame(s) via the image-selector layer, fill ``reference_frames`` and
      ``binding_hints.reference_image_paths``, then validate the artifact.
    """

    name = "character_consistency_builder"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "character_animation"
    provider = "openmontage"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=100, network_required=True)
    agent_skills = ["character-consistency", "character-rigging", "flux-best-practices"]
    capabilities = [
        "draft_character_consistency",
        "generate_character_anchor_frames",
        "bind_character_refs_for_video_gen",
    ]
    best_for = [
        "Keeping one character's appearance consistent across many cloud-generated scenes",
        "Binding per-character reference images into seedance/veo/higgsfield video generation",
    ]
    not_good_for = [
        "Local rigged (SVG/Canvas) character animation — use character_spec_generator",
        "Inline per-request cloning without a persistent anchor",
    ]
    input_schema = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["build", "generate_frames"],
                "default": "build",
            },
            "characters": {"type": "array", "description": "Character specs (id, role, appearance, reference_prompt, views)"},
            "style": {"type": "object"},
            "views": {"type": "array", "items": {"type": "string"}, "description": "Anchor views to generate per character (default ['front'])"},
            "aspect_ratio": {"type": "string", "description": "Reference frame aspect ratio for image gen (e.g. 16:9, 9:16, 1:1)"},
            "image_provider": {"type": "string", "description": "Preferred image-selector provider for anchor frames"},
            "output_dir": {"type": "string", "description": "Directory to write reference frames (projects/<p>/assets/characters)"},
            "output_path": {"type": "string", "description": "Where to write the character_consistency JSON"},
        },
    }
    output_schema = {"type": "object", "properties": {"character_consistency": {"type": "object"}}}
    artifact_schema = {"artifact": "character_consistency"}
    side_effects = ["writes reference frame images under output_dir", "optionally writes character_consistency JSON"]
    user_visible_verification = ["Review each character's anchor frames for identity consistency before binding"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        operation = inputs.get("operation", "build")

        artifact = self._build_artifact(inputs)

        if operation == "generate_frames":
            self._generate_frames(inputs, artifact)

        # Validate the artifact against the schema (raises on failure)
        try:
            validate_artifact("character_consistency", artifact)
        except Exception as exc:
            return ToolResult(success=False, error=f"character_consistency invalid: {exc}")

        artifacts = _write_json(inputs.get("output_path"), artifact)
        return ToolResult(
            success=True,
            data={
                "character_consistency": artifact,
                "characters": [c["id"] for c in artifact["characters"]],
            },
            artifacts=artifacts,
            duration_seconds=round(time.time() - start, 2),
        )

    def _build_artifact(self, inputs: dict[str, Any]) -> dict[str, Any]:
        raw_characters = inputs.get("characters") or []
        if not raw_characters:
            raw_characters = [
                {
                    "id": "protagonist",
                    "role": "lead character",
                    "appearance": "A mid-30s man with short dark hair, calm expression, navy jacket, clean-shaven.",
                    "reference_prompt": "",
                }
            ]

        style = inputs.get("style", {}) if isinstance(inputs.get("style"), dict) else {}
        visual_style = style.get("visual_style") or "cinematic realism"

        characters: list[dict[str, Any]] = []
        for raw in raw_characters:
            cid = _slug(str(raw.get("id") or raw.get("name") or raw.get("display_name") or "character"))
            appearance = str(raw.get("appearance", "")).strip()
            reference_prompt = raw.get("reference_prompt") or self._compose_prompt(appearance, visual_style)
            characters.append(
                {
                    "id": cid,
                    "display_name": raw.get("display_name") or str(raw.get("id", cid)).replace("_", " ").title(),
                    "role": raw.get("role", "supporting character"),
                    "appearance": appearance,
                    "reference_prompt": reference_prompt,
                    "reference_frames": raw.get("reference_frames", []),
                    "binding_hints": raw.get("binding_hints", {}),
                }
            )

        return {
            "version": "1.0",
            "style": {
                "visual_style": visual_style,
                "palette": style.get("palette", []),
                "render_notes": style.get("render_notes", ""),
            },
            "characters": characters,
            "metadata": {
                "source": "character_consistency_builder",
                "intended_video_providers": ["seedance_video", "veo_video", "higgsfield_video", "minimax_video"],
            },
        }

    @staticmethod
    def _compose_prompt(appearance: str, visual_style: str) -> str:
        return (
            f"{visual_style}. Consistent character portrait: {appearance} "
            "centered, full upper body, plain neutral background, even soft lighting, "
            "sharp focus, reference-quality identity shot, no text, no watermark."
        )

    def _generate_frames(self, inputs: dict[str, Any], artifact: dict[str, Any]) -> None:
        """Generate anchor frames via the image-selector layer."""
        try:
            from tools.tool_registry import registry

            registry.ensure_discovered()
            selectors = [t for t in registry.get_by_capability("image_generation")]
            image_selector = next((t for t in selectors if t.name == "image_selector"), None)
        except Exception:
            image_selector = None

        if image_selector is None:
            return  # leave reference_frames empty; downstream skills handle the binding

        views = inputs.get("views") or ["front"]
        aspect_ratio = inputs.get("aspect_ratio", "16:9")
        output_dir = Path(inputs.get("output_dir") or "assets/characters")
        output_dir.mkdir(parents=True, exist_ok=True)

        for char in artifact["characters"]:
            if char.get("reference_frames"):
                continue  # don't regenerate existing anchors
            ref_paths: list[str] = []
            for view in views:
                prompt = char["reference_prompt"]
                if view != "front":
                    prompt = f"{prompt} (view: {view})"
                out_path = str(output_dir / f"{char['id']}-{view}.png")
                params: dict[str, Any] = {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_path": out_path,
                }
                if inputs.get("image_provider"):
                    params["preferred_provider"] = inputs["image_provider"]
                try:
                    result = image_selector.execute(params)
                except Exception:
                    continue
                if not result.success:
                    continue
                frame = {
                    "view": view,
                    "path": out_path,
                    "source_tool": "image_selector",
                }
                if result.data.get("model") is not None:
                    frame["model"] = result.data.get("model")
                if result.data.get("seed") is not None:
                    frame["seed"] = result.data.get("seed")
                if result.data.get("qa_score") is not None:
                    frame["qa_score"] = result.data.get("qa_score")
                char.setdefault("reference_frames", []).append(frame)
                ref_paths.append(out_path)

            hints = char.setdefault("binding_hints", {})
            hints["reference_image_paths"] = ref_paths
            hints.setdefault("preferred_providers", ["seedance_video", "veo_video", "higgsfield_video"])
            if ref_paths:
                hints["first_frame_path"] = ref_paths[0]
