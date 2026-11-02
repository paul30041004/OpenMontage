"""Long-form scene breakdown and deterministic chunk assembly tool.

Orchestrates 2-hour / multi-scene long-form productions by bridging OpenMontage's
narrative hierarchy (Acts -> Sequences -> Scenes -> Shots) with MiniMax H3
long-video latent chaining (ComfyUI-H3-Long-Video / Herrgotts) and Remotion
chunked timeline composition.

Core Invariants (HEPHAESTUS-METATRON Long-Form Engine):
1. OpenMontage is the Orchestrator; H3 Long-Form is the Shot Generator.
2. 2-Hour content must be broken down into discrete Scenes (30-90s continuous shots max).
3. Scene Boundary Root Reset: Latent chaining is NEVER allowed across scene boundaries.
   Every new scene must hard-reset its latent to a clean Ref2VA anchor + Style Bible token.
4. Chunked Rendering: 2-hour master timeline is split into 5-10 min sequence chunks
   to prevent VRAM/RAM exhaustion, followed by lossless concatenation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)


class LongformSceneAssembler(BaseTool):
    name = "longform_scene_assembler"
    version = "1.0.0"
    tier = ToolTier.GENERATE
    capability = "longform_orchestration"
    provider = "openmontage"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg", "cmd:ffprobe"]
    install_instructions = "Requires FFmpeg for timeline chunk validation and assembly."
    agent_skills = ["comfyui", "minimax-h3", "remotion-best-practices"]

    capabilities = [
        "plan_hierarchy",
        "enforce_scene_root_reset",
        "build_comfyui_h3_payloads",
        "assemble_timeline_chunks",
    ]
    supports = {
        "two_hour_capacity": True,
        "scene_root_reset": True,
        "comfyui_api_format": True,
        "chunked_rendering": True,
        "multitrack_audio": True,
    }
    best_for = [
        "2-hour feature film and documentary scene breakdown and shot budgeting",
        "MiniMax H3 ComfyUI long-form latent chaining orchestration with drift mitigation",
        "Multi-sequence chunked Remotion / FFmpeg timeline assembly",
    ]
    not_good_for = [
        "Single-clip 15-second shorts (use short-form-factory directly)",
        "Raw continuous 2-hour unedited single-shot generation (physically impossible/undesirable)",
    ]

    input_schema = {
        "type": "object",
        "required": ["operation"],
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "plan_hierarchy",
                    "build_comfyui_h3_payloads",
                    "assemble_timeline_chunks",
                ],
                "description": "Long-form orchestration operation",
            },
            # Parameters for plan_hierarchy
            "target_duration_minutes": {
                "type": "number",
                "minimum": 5.0,
                "maximum": 240.0,
                "default": 120.0,
                "description": "Total target duration in minutes (e.g. 120 for 2-hour film)",
            },
            "pacing": {
                "type": "string",
                "enum": ["fast", "cinematic_standard", "slow_burn"],
                "default": "cinematic_standard",
                "description": "Pacing profile determining average scene and shot lengths",
            },
            "title": {
                "type": "string",
                "default": "Untitled Feature",
            },
            "story_bible": {
                "type": "object",
                "description": "Optional story bible carrying characters and visual tokens",
            },
            # Parameters for build_comfyui_h3_payloads
            "scene_list": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of planned scenes with duration, setting, and characters",
            },
            "workflow_template_path": {
                "type": "string",
                "description": "Path to ComfyUI API-format JSON workflow for MiniMax H3",
            },
            "output_node_id": {
                "type": "string",
                "default": "16",
                "description": "ComfyUI output node ID (e.g. SaveVideo / VHS_VideoCombine)",
            },
            # Parameters for assemble_timeline_chunks
            "rendered_chunks": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of rendered sequence/scene chunk file paths",
            },
            "audio_stems": {
                "type": "object",
                "description": "Paths to dialogue, sfx, and bgm tracks",
            },
            "output_path": {
                "type": "string",
                "description": "Path to save master timeline or assembled video",
            },
        },
    }

    # Standard 3-Act / 8-Sequence dramatic distribution percentages
    SEQUENCE_DISTRIBUTION = [
        {"seq": 1, "act": "Act 1", "name": "Status Quo & Inciting Incident", "pct": 0.125},
        {"seq": 2, "act": "Act 1", "name": "Predicament & Lock-In (Plot Point 1)", "pct": 0.125},
        {"seq": 3, "act": "Act 2A", "name": "First Obstacles & Exploration", "pct": 0.125},
        {"seq": 4, "act": "Act 2A", "name": "Rising Stakes & Midpoint Shift", "pct": 0.125},
        {"seq": 5, "act": "Act 2B", "name": "Rising Pressure & Counter-Attack", "pct": 0.125},
        {"seq": 6, "act": "Act 2B", "name": "All is Lost (Dark Night of Soul)", "pct": 0.125},
        {"seq": 7, "act": "Act 3", "name": "Climax Build & Final Confrontation", "pct": 0.125},
        {"seq": 8, "act": "Act 3", "name": "Resolution & New Equilibrium", "pct": 0.125},
    ]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        operation = inputs.get("operation")
        if operation == "plan_hierarchy":
            return self._plan_hierarchy(inputs)
        elif operation == "build_comfyui_h3_payloads":
            return self._build_comfyui_h3_payloads(inputs)
        elif operation == "assemble_timeline_chunks":
            return self._assemble_timeline_chunks(inputs)
        else:
            return ToolResult(
                success=False,
                error=f"Unsupported operation: {operation!r}",
            )

    # -------------------------------------------------------------------------
    # 1. PLAN HIERARCHY (Act -> Sequence -> Scene -> Shot Breakdown)
    # -------------------------------------------------------------------------
    def _plan_hierarchy(self, inputs: dict[str, Any]) -> ToolResult:
        target_minutes = float(inputs.get("target_duration_minutes", 120.0))
        total_seconds = target_minutes * 60.0
        pacing = inputs.get("pacing", "cinematic_standard")
        title = inputs.get("title", "Untitled Feature")

        # Pacing dials: average scene length in seconds
        pacing_table = {
            "fast": {"avg_scene_sec": 75.0, "max_shot_sec": 30.0},
            "cinematic_standard": {"avg_scene_sec": 120.0, "max_shot_sec": 60.0},
            "slow_burn": {"avg_scene_sec": 200.0, "max_shot_sec": 90.0},
        }
        cfg = pacing_table.get(pacing, pacing_table["cinematic_standard"])
        avg_scene = cfg["avg_scene_sec"]
        max_shot = cfg["max_shot_sec"]

        total_scenes_estimated = max(8, round(total_seconds / avg_scene))
        scenes_per_seq = max(1, round(total_scenes_estimated / 8))

        sequences = []
        global_scene_idx = 1
        global_time_acc = 0.0

        for seq_def in self.SEQUENCE_DISTRIBUTION:
            seq_num = seq_def["seq"]
            seq_duration = total_seconds * seq_def["pct"]
            scene_duration = seq_duration / scenes_per_seq

            seq_scenes = []
            for s_idx in range(scenes_per_seq):
                scene_id = f"seq{seq_num:02d}_sc{s_idx + 1:02d}"
                start_sec = global_time_acc
                end_sec = global_time_acc + scene_duration
                global_time_acc = end_sec

                # Plan in-scene continuous shot chaining
                # H3 long-video nodes chain 30-90s continuous shots.
                shot_count = max(1, math.ceil(scene_duration / max_shot))
                shot_dur = scene_duration / shot_count

                shots = []
                for sh_idx in range(shot_count):
                    is_root = (sh_idx == 0)
                    shot_id = f"{scene_id}_sh{sh_idx + 1:02d}"
                    shots.append({
                        "shot_id": shot_id,
                        "duration_seconds": round(shot_dur, 2),
                        "latent_mode": "root_anchor" if is_root else "chained_latent",
                        "fl2va_quality_reset": is_root or (sh_idx % 3 == 0),
                        "scene_boundary_reset": is_root,
                    })

                seq_scenes.append({
                    "scene_id": scene_id,
                    "scene_number": global_scene_idx,
                    "act": seq_def["act"],
                    "sequence_number": seq_num,
                    "sequence_name": seq_def["name"],
                    "start_seconds": round(start_sec, 2),
                    "end_seconds": round(end_sec, 2),
                    "duration_seconds": round(scene_duration, 2),
                    "shots": shots,
                    # INVIOLABLE RULE: Every scene boundary mandates a latent root reset
                    "scene_boundary_root_reset": True,
                    "latent_chaining_policy": (
                        "IN-SCENE ONLY. Reset root latent at scene boundary using Ref2VA anchor."
                    ),
                })
                global_scene_idx += 1

            sequences.append({
                "sequence_number": seq_num,
                "act": seq_def["act"],
                "name": seq_def["name"],
                "target_duration_seconds": round(seq_duration, 2),
                "scene_count": len(seq_scenes),
                "scenes": seq_scenes,
            })

        breakdown = {
            "title": title,
            "target_duration_minutes": target_minutes,
            "total_duration_seconds": total_seconds,
            "pacing": pacing,
            "total_acts": 3,
            "total_sequences": len(sequences),
            "total_scenes": global_scene_idx - 1,
            "sequences": sequences,
            "drift_mitigation_contract": {
                "max_continuous_chain_seconds": max_shot * 2,
                "scene_boundary_root_reset": "ENFORCED",
                "recommended_generator": "comfyui_video with minimax_h3_local / ComfyUI-H3-Long-Video",
            },
        }

        return ToolResult(
            success=True,
            data=breakdown,
            artifacts=[],
        )

    # -------------------------------------------------------------------------
    # 2. BUILD COMFYUI H3 PAYLOADS (Ref2VA Anchor & Latent Chaining Injection)
    # -------------------------------------------------------------------------
    def _build_comfyui_h3_payloads(self, inputs: dict[str, Any]) -> ToolResult:
        scene_list = inputs.get("scene_list", [])
        workflow_path = inputs.get("workflow_template_path")
        output_node = inputs.get("output_node_id", "16")
        story_bible = inputs.get("story_bible", {})

        style_tokens = story_bible.get("visual_style_tokens", "cinematic lighting, photoreal 35mm")
        characters = {c["id"]: c for c in story_bible.get("characters", [])}

        generated_payloads = []

        for sc in scene_list:
            scene_id = sc.get("scene_id", "scene_01")
            prompt_base = sc.get("prompt", sc.get("description", "Cinematic scene"))
            duration = sc.get("duration_seconds", 60.0)
            char_ids = sc.get("character_ids", [])
            char_prompts = [characters[cid]["appearance"] for cid in char_ids if cid in characters]

            full_prompt = f"{prompt_base}. Characters: {', '.join(char_prompts)}. Style: {style_tokens}"
            ref_image = sc.get("reference_image_path") or (
                characters[char_ids[0]].get("anchor_image") if char_ids and char_ids[0] in characters else None
            )

            # Build in-scene shot chaining sequence
            shots = sc.get("shots", [])
            if not shots:
                shots = [{"shot_id": f"{scene_id}_sh01", "duration_seconds": duration, "latent_mode": "root_anchor"}]

            shot_payloads = []
            for s_idx, shot in enumerate(shots):
                is_root = (s_idx == 0)
                shot_payload = {
                    "shot_id": shot.get("shot_id"),
                    "duration": shot.get("duration_seconds", 30.0),
                    "model_family": "minimax_h3_local",
                    "operation": "image_to_video" if ref_image else "text_to_video",
                    "prompt": full_prompt,
                    "reference_image_path": ref_image,
                    "output_node": output_node,
                    "latent_chaining": {
                        "is_root": is_root,
                        "chain_from_previous": not is_root,
                        "reset_reason": "scene_boundary_root_reset" if is_root else "none",
                        "fl2va_quality_reset": shot.get("fl2va_quality_reset", is_root),
                    },
                }
                if workflow_path:
                    shot_payload["workflow_path"] = workflow_path

                shot_payloads.append(shot_payload)

            generated_payloads.append({
                "scene_id": scene_id,
                "scene_boundary_reset": True,
                "shot_count": len(shot_payloads),
                "shot_payloads": shot_payloads,
            })

        return ToolResult(
            success=True,
            data={
                "scene_count": len(generated_payloads),
                "total_shot_payloads": sum(p["shot_count"] for p in generated_payloads),
                "scenes": generated_payloads,
            },
        )

    # -------------------------------------------------------------------------
    # 3. ASSEMBLE TIMELINE CHUNKS (Remotion Multi-Track Chunk Assembly)
    # -------------------------------------------------------------------------
    def _assemble_timeline_chunks(self, inputs: dict[str, Any]) -> ToolResult:
        rendered_chunks = inputs.get("rendered_chunks", [])
        audio_stems = inputs.get("audio_stems", {})
        output_path = inputs.get("output_path", "projects/longform_master.json")

        if not rendered_chunks:
            return ToolResult(
                success=False,
                error="No rendered_chunks provided for assembly.",
            )

        timeline_segments = []
        current_time = 0.0

        for chunk in rendered_chunks:
            chunk_id = chunk.get("id", chunk.get("scene_id", "chunk"))
            path = chunk.get("path")
            dur = float(chunk.get("duration_seconds", 60.0))
            timeline_segments.append({
                "id": chunk_id,
                "file_path": path,
                "start_seconds": round(current_time, 2),
                "end_seconds": round(current_time + dur, 2),
                "duration_seconds": round(dur, 2),
                "transition_out": chunk.get("transition_out", "dissolve"),
            })
            current_time += dur

        edit_decisions = {
            "version": "1.0",
            "render_runtime": "remotion",
            "composition_mode": "chunked_feature_film",
            "total_duration_seconds": round(current_time, 2),
            "video_tracks": [
                {
                    "track_id": "video_master",
                    "clips": timeline_segments,
                }
            ],
            "audio_tracks": [
                {
                    "track_id": "dialogue_stem",
                    "source": audio_stems.get("dialogue"),
                    "target_level_db": -3.0,
                },
                {
                    "track_id": "sfx_stem",
                    "source": audio_stems.get("sfx"),
                    "target_level_db": -12.0,
                },
                {
                    "track_id": "bgm_bed",
                    "source": audio_stems.get("bgm"),
                    "target_level_db": -18.0,
                    "ducking": {
                        "enabled": True,
                        "duck_level_db": -24.0,
                        "threshold_db": -20.0,
                    },
                },
            ],
            "chunk_render_plan": {
                "chunk_size_minutes": 10.0,
                "estimated_chunks": math.ceil((current_time / 60.0) / 10.0),
                "final_concat": "ffmpeg_concat_demuxer",
            },
        }

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(edit_decisions, indent=2), encoding="utf-8")

        return ToolResult(
            success=True,
            data={
                "edit_decisions_path": str(out_file),
                "total_duration_seconds": round(current_time, 2),
                "total_chunks": len(timeline_segments),
                "assembly_method": "Remotion multi-track with FFmpeg lossless chunk concat",
            },
            artifacts=[str(out_file)],
        )
