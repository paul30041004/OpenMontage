"""Contract tests for LongformSceneAssembler (HEPHAESTUS-METATRON 2-Hour Engine).

Validates hierarchical scene breakdown, Scene Boundary Root Reset enforcement,
MiniMax H3 ComfyUI payload generation, and Remotion chunked timeline assembly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.base_tool import BaseTool, ToolRuntime, ToolTier
from tools.tool_registry import registry
from tools.video.longform_scene_assembler import LongformSceneAssembler


class TestContract:
    def test_inherits_base_tool(self):
        assert issubclass(LongformSceneAssembler, BaseTool)

    def test_identity(self):
        tool = LongformSceneAssembler()
        assert tool.name == "longform_scene_assembler"
        assert tool.capability == "longform_orchestration"
        assert tool.provider == "openmontage"
        assert tool.tier == ToolTier.GENERATE
        assert tool.runtime == ToolRuntime.LOCAL

    def test_layer_three_skills_resolve(self):
        root = Path(__file__).resolve().parents[2] / ".agents" / "skills"
        tool = LongformSceneAssembler()
        for skill in tool.agent_skills:
            assert (root / skill / "SKILL.md").exists(), f"Missing Layer 3 skill: {skill}"

    def test_discovered_by_registry(self):
        registry.discover()
        names = [t.name for t in registry.get_by_capability("longform_orchestration")]
        assert "longform_scene_assembler" in names


class TestHierarchyPlanning:
    def test_two_hour_breakdown_math(self):
        tool = LongformSceneAssembler()
        result = tool.execute({
            "operation": "plan_hierarchy",
            "target_duration_minutes": 120.0,
            "pacing": "cinematic_standard",
            "title": "Cosmic Forge Feature",
        })

        assert result.success is True
        data = result.data
        assert data["target_duration_minutes"] == 120.0
        assert data["total_duration_seconds"] == 7200.0
        assert data["total_acts"] == 3
        assert len(data["sequences"]) == 8

        # Verify Scene Boundary Root Reset is strictly enforced for every scene
        total_scenes = 0
        for seq in data["sequences"]:
            assert seq["target_duration_seconds"] == 900.0  # 15 min per sequence
            for sc in seq["scenes"]:
                total_scenes += 1
                assert sc["scene_boundary_root_reset"] is True
                assert "IN-SCENE ONLY" in sc["latent_chaining_policy"]

                # First shot must be root_anchor; subsequent shots chained
                shots = sc["shots"]
                assert len(shots) >= 1
                assert shots[0]["latent_mode"] == "root_anchor"
                assert shots[0]["scene_boundary_reset"] is True
                for subsequent_shot in shots[1:]:
                    assert subsequent_shot["latent_mode"] == "chained_latent"

        assert data["total_scenes"] == total_scenes
        assert total_scenes >= 40

    def test_short_feature_pacing(self):
        tool = LongformSceneAssembler()
        result = tool.execute({
            "operation": "plan_hierarchy",
            "target_duration_minutes": 15.0,
            "pacing": "fast",
            "title": "15-Minute Short",
        })

        assert result.success is True
        assert result.data["total_duration_seconds"] == 900.0
        assert len(result.data["sequences"]) == 8


class TestComfyUIH3PayloadGeneration:
    def test_payload_generation_with_ref2va_and_tokens(self):
        tool = LongformSceneAssembler()
        sample_scenes = [
            {
                "scene_id": "sc_01",
                "description": "Detective enters dimly lit apartment",
                "duration_seconds": 60.0,
                "character_ids": ["char_detective"],
                "shots": [
                    {"shot_id": "sc_01_sh01", "duration_seconds": 30.0},
                    {"shot_id": "sc_01_sh02", "duration_seconds": 30.0},
                ],
            }
        ]
        sample_bible = {
            "visual_style_tokens": "Neo-noir, anamorphic lens flare, rain-soaked 35mm",
            "characters": [
                {
                    "id": "char_detective",
                    "appearance": "Kang, 40s weary detective in dark trench coat",
                    "anchor_image": "assets/characters/detective_anchor.png",
                }
            ],
        }

        result = tool.execute({
            "operation": "build_comfyui_h3_payloads",
            "scene_list": sample_scenes,
            "workflow_template_path": "tools/_comfyui/workflows/h3-longform-api.template.json",
            "output_node_id": "16",
            "story_bible": sample_bible,
        })

        assert result.success is True
        scenes = result.data["scenes"]
        assert len(scenes) == 1
        scene_payload = scenes[0]
        assert scene_payload["scene_boundary_reset"] is True

        shots = scene_payload["shot_payloads"]
        assert len(shots) == 2

        # Shot 1: Root latent, scene boundary reset
        sh1 = shots[0]
        assert sh1["shot_id"] == "sc_01_sh01"
        assert sh1["model_family"] == "minimax_h3_local"
        assert sh1["output_node"] == "16"
        assert sh1["reference_image_path"] == "assets/characters/detective_anchor.png"
        assert sh1["latent_chaining"]["is_root"] is True
        assert sh1["latent_chaining"]["reset_reason"] == "scene_boundary_root_reset"
        assert "Neo-noir" in sh1["prompt"]
        assert "Kang" in sh1["prompt"]

        # Shot 2: Chained latent from previous shot, no root reset
        sh2 = shots[1]
        assert sh2["shot_id"] == "sc_01_sh02"
        assert sh2["latent_chaining"]["is_root"] is False
        assert sh2["latent_chaining"]["chain_from_previous"] is True
        assert sh2["latent_chaining"]["reset_reason"] == "none"


class TestTimelineChunkAssembly:
    def test_remotion_chunked_timeline_assembly(self, tmp_path):
        tool = LongformSceneAssembler()
        rendered_chunks = [
            {"id": "seq_01", "path": "renders/seq_01.mp4", "duration_seconds": 600.0},
            {"id": "seq_02", "path": "renders/seq_02.mp4", "duration_seconds": 600.0},
        ]
        audio_stems = {
            "dialogue": "assets/audio/dialogue_master.wav",
            "sfx": "assets/audio/sfx_master.wav",
            "bgm": "assets/audio/score_master.wav",
        }
        output_file = tmp_path / "longform_master.json"

        result = tool.execute({
            "operation": "assemble_timeline_chunks",
            "rendered_chunks": rendered_chunks,
            "audio_stems": audio_stems,
            "output_path": str(output_file),
        })

        assert result.success is True
        assert result.data["total_duration_seconds"] == 1200.0
        assert output_file.exists()

        content = json.loads(output_file.read_text(encoding="utf-8"))
        assert content["render_runtime"] == "remotion"
        assert content["composition_mode"] == "chunked_feature_film"
        assert content["total_duration_seconds"] == 1200.0

        # Verify multi-track audio stem structure and ducking
        tracks = {t["track_id"]: t for t in content["audio_tracks"]}
        assert "dialogue_stem" in tracks
        assert tracks["dialogue_stem"]["target_level_db"] == -3.0
        assert "bgm_bed" in tracks
        assert tracks["bgm_bed"]["ducking"]["enabled"] is True
