"""Contract tests for the Three.js code-video proxy tool.

Runs without network and without paid APIs. Rendering tests run only when a
Chrome/Chromium binary and FFmpeg are present; otherwise the degraded
authoring path is asserted instead.
"""

import json
import shutil

import pytest

from tools.base_tool import BaseTool, ToolRuntime, ToolStability, ToolTier
from tools.graphics.threejs_proxy import ThreeJSProxy, _find_chrome
from tools.tool_registry import registry


def _scene(prompt="proxy test shot"):
    return {
        "operation": "build",
        "prompt": prompt,
        "shot_spec": {"duration": 2, "width": 640, "height": 360, "fps": 12},
        "scene_spec": {
            "background": "#0b1020",
            "ground": {"enabled": True, "size": 120, "color": "#1c2433", "grid": True},
            "objects": [
                {
                    "id": "hero-car",
                    "kind": "car",
                    "position": [0, 0.4, 0],
                    "color": "#b8312a",
                    "motion": {
                        "kind": "linear",
                        "from": [-8, 0.4, 0],
                        "to": [8, 0.4, 10],
                        "t0": 0,
                        "t1": 2,
                    },
                },
                {
                    "id": "marker",
                    "kind": "sphere",
                    "position": [0, 4, -6],
                    "size": {"r": 1.2},
                    "color": "#f2c230",
                    "motion": {"kind": "static"},
                },
            ],
            "camera": {
                "mode": "keys",
                "fov": 50,
                "keys": [
                    {"t": 0, "pos": [-10, 5, 16], "look": [0, 1, 0]},
                    {"t": 2, "pos": [10, 5, 16], "look": [0, 1, 0]},
                ],
            },
        },
        "seed": 7,
    }


class TestContract:
    def test_inherits_base_tool(self):
        assert issubclass(ThreeJSProxy, BaseTool)

    def test_identity(self):
        tool = ThreeJSProxy()
        assert tool.name == "threejs_proxy"
        assert tool.provider == "threejs"
        assert tool.capability == "motion_proxy"
        assert tool.tier == ToolTier.GENERATE
        assert tool.runtime == ToolRuntime.LOCAL
        assert tool.stability == ToolStability.BETA

    def test_layer_three_skills_resolve(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[2] / ".agents" / "skills"
        for skill in ThreeJSProxy().agent_skills:
            assert (root / skill / "SKILL.md").exists(), skill

    def test_discovered_with_motion_proxy_capability(self):
        registry.discover()
        names = [t.name for t in registry.get_by_capability("motion_proxy")]
        assert "threejs_proxy" in names


class TestValidation:
    def test_rejects_empty_prompt(self):
        r = ThreeJSProxy().execute({"operation": "build", "prompt": "  "})
        assert not r.success and "prompt" in r.error

    def test_rejects_unknown_operation(self):
        r = ThreeJSProxy().execute({"operation": "teleport", "prompt": "x"})
        assert not r.success

    def test_rejects_bad_camera_keys(self):
        spec = _scene()
        spec["scene_spec"]["camera"]["keys"] = [{"t": 1, "pos": [0, 0, 0], "look": [0, 0, 0]}]
        r = ThreeJSProxy().execute(spec)
        assert not r.success

    def test_rejects_unknown_object_kind(self):
        spec = _scene()
        spec["scene_spec"]["objects"][0]["kind"] = "spaceship"
        r = ThreeJSProxy().execute(spec)
        assert not r.success and "spaceship" in r.error

    def test_validate_op_returns_spec_without_files(self, tmp_path):
        spec = _scene()
        spec["operation"] = "validate"
        r = ThreeJSProxy().execute(spec)
        assert r.success
        assert r.data["spec"]["shot"]["duration"] == 2
        assert list(tmp_path.iterdir()) == []

    def test_build_requires_output_path(self):
        r = ThreeJSProxy().execute(_scene())  # no output_path key
        assert not r.success and "output_path" in r.error


class TestBuild:
    def test_build_materializes_editable_workspace(self, tmp_path):
        spec = _scene()
        spec["output_path"] = str(tmp_path / "ws")
        r = ThreeJSProxy().execute(spec)
        assert r.success, r.error
        root = tmp_path / "ws"
        for name in ("index.html", "scene.js", "scene-spec.js", "scene.json",
                     "three.module.min.js", "motion_proxy.json"):
            assert (root / name).exists(), name
        scene = json.loads((root / "scene.json").read_text())
        assert scene["shot"]["fps"] == 12
        assert [o["id"] for o in scene["scene"]["objects"]] == ["hero-car", "marker"]
        artifact = json.loads((root / "motion_proxy.json").read_text())
        assert artifact["version"] == "1.0"
        assert artifact["provider_hints"]["suggested_operation"] == "reference_to_video"
        assert r.data["artifact_path"].endswith("motion_proxy.json")

    @pytest.mark.skipif(
        _find_chrome() is None or shutil.which("ffmpeg") is None,
        reason="needs Chrome/Chromium + FFmpeg",
    )
    def test_build_renders_proxy_and_reference_frame(self, tmp_path):
        spec = _scene()
        spec["output_path"] = str(tmp_path / "ws")
        r = ThreeJSProxy().execute(spec)
        assert r.success, r.error
        assert r.data["rendered"] is True
        proxy = tmp_path / "ws" / "renders" / "proxy.mp4"
        frame = tmp_path / "ws" / "reference_frame.png"
        assert proxy.exists() and proxy.stat().st_size > 10_000
        assert frame.exists() and frame.stat().st_size > 5_000
        assert frame.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
