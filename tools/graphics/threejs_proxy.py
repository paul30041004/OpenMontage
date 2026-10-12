"""Code-video proxy: text prompt -> editable Three.js scene -> rendered proxy clip.

CodeVideoModel-style motion control for OpenMontage video generation. An
editable, deterministic Three.js scene package is rendered headlessly into a
short proxy MP4 plus a first-frame reference still. Downstream, the agent feeds
``proxy_video`` + ``reference_frame`` into ``video_selector`` with
``operation="reference_to_video"`` (``h3_max_video`` / ``minimax_video`` /
``seedance_video`` / ``kling_official_video`` / ``wan_*`` / ``runway_video`` /
``atlas_video``) — the same role CodeVideoModel's code video + reference image
play for MiniMax-H3.

The agent owns creative planning (prompt -> shot/scene spec). This tool
validates + normalizes the spec, materializes the editable workspace, renders
deterministically when a Chrome/Chromium binary and FFmpeg are present, and
emits a ``motion_proxy`` artifact validated against
``schemas/artifacts/motion_proxy.schema.json``.

When no renderer is available the build still succeeds as authoring
(workspace + spec + render instructions); ``rendered`` is False and the agent
renders later via ``video_compose`` / ``hyperframes_compose``.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)

TEMPLATE_DIR = Path(__file__).parent / "templates" / "threejs_proxy"

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_OBJECT_KINDS = {"box", "sphere", "cylinder", "cone", "torus", "plane", "car"}
_MOTION_KINDS = {"static", "linear", "circular"}
_CAMERA_MODES = {"keys", "orbit"}
_FPS_CHOICES = {12, 24, 30}
MAX_OBJECTS = 64
MAX_KEYS = 40


def _number(value: Any, default: float) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def _integer(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _vec(value: Any, length: int, default: list[float]) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != length:
        return list(default)
    return [_number(component, default[index]) for index, component in enumerate(value)]


def _color(value: Any, default: str) -> str:
    text = str(value or "")
    return text if _HEX.fullmatch(text) else default


def _slug(value: Any, fallback: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return text or fallback


def _find_chrome() -> str | None:
    override = os.environ.get("CHROME_BIN") or os.environ.get("CHROME_PATH")
    if override and Path(override).exists():
        return override
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    if sys.platform == "darwin":
        app = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if app.exists():
            return str(app)
    roots = []
    if sys.platform == "darwin":
        roots.append(Path.home() / "Library" / "Caches" / "ms-playwright")
    else:
        roots.append(Path.home() / ".cache" / "ms-playwright")
    for root in roots:
        if not root.exists():
            continue
        for candidate in sorted(root.glob("chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium")):
            return str(candidate)
        for candidate in sorted(root.glob("chromium-*/chrome-linux/chrome")):
            return str(candidate)
        for candidate in sorted(root.glob("chromium_headless_shell-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium")):
            return str(candidate)
        for candidate in sorted(root.glob("chromium_headless_shell-*/chrome-linux/headless_shell")):
            return str(candidate)
    return None


_SCENE_JS = r"""import * as THREE from './three.module.min.js';

const SPEC = window.__SCENE__;

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

let renderer = null;
let scene = null;
let camera = null;
let actors = [];

function mat(color, metalness, roughness) {
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    metalness: metalness,
    roughness: roughness,
  });
}

function buildCar(spec, m) {
  const g = new THREE.Group();
  const body = spec.body || {};
  const bw = body.w || 2.2, bh = body.h || 0.6, bd = body.d || 4.2;
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, bd), m);
  mesh.position.y = (spec.wheelR || 0.4) + bh / 2;
  g.add(mesh);
  const cabin = spec.cabin || {};
  const cab = new THREE.Mesh(
    new THREE.BoxGeometry(cabin.w || bw * 0.55, cabin.h || 0.55, cabin.d || bd * 0.45),
    mat(spec.cabinColor || "#9fb4c8", 0.1, 0.35)
  );
  cab.position.set(0, mesh.position.y + bh / 2 + (cabin.h || 0.55) / 2, -(bd * 0.05));
  g.add(cab);
  const wheels = [];
  const wr = spec.wheelR || 0.4;
  const wg = new THREE.CylinderGeometry(wr, wr, 0.35, 20);
  wg.rotateZ(Math.PI / 2);
  const wm = mat("#1a1a1a", 0.2, 0.8);
  for (const [x, z] of [[-bw / 2, bd / 2 - wr], [bw / 2, bd / 2 - wr], [-bw / 2, -bd / 2 + wr], [bw / 2, -bd / 2 + wr]]) {
    const w = new THREE.Mesh(wg, wm);
    w.position.set(x, wr, z);
    g.add(w);
    wheels.push(w);
  }
  g.userData.wheels = wheels;
  return g;
}

function buildObject(spec) {
  const m = mat(spec.color || "#8a8f98", spec.metalness ?? 0.1, spec.roughness ?? 0.7);
  const s = spec.size || {};
  let obj;
  switch (spec.kind) {
    case "sphere": obj = new THREE.Mesh(new THREE.SphereGeometry(s.r || 1, 40, 28), m); break;
    case "cylinder": obj = new THREE.Mesh(new THREE.CylinderGeometry(s.rt ?? 1, s.rb ?? 1, s.h || 2, 32), m); break;
    case "cone": obj = new THREE.Mesh(new THREE.ConeGeometry(s.r || 1, s.h || 2, 32), m); break;
    case "torus": obj = new THREE.Mesh(new THREE.TorusGeometry(s.r || 1.4, s.tube || 0.35, 20, 48), m); break;
    case "plane": obj = new THREE.Mesh(new THREE.PlaneGeometry(s.w || 10, s.h || 10), m); break;
    case "car": return buildCar(spec, m);
    default: obj = new THREE.Mesh(new THREE.BoxGeometry(s.w || 1.5, s.h || 1.5, s.d || 1.5), m);
  }
  return obj;
}

function applyMotion(obj, motion, t) {
  if (!motion || motion.kind === "static") return;
  if (motion.kind === "linear") {
    const from = motion.from || [0, 0, 0];
    const to = motion.to || [0, 0, 0];
    const t0 = motion.t0 ?? 0, t1 = motion.t1 ?? 1;
    const p = Math.min(1, Math.max(0, (t - t0) / Math.max(1e-6, t1 - t0)));
    const e = p * p * (3 - 2 * p);
    obj.position.set(
      from[0] + (to[0] - from[0]) * e,
      from[1] + (to[1] - from[1]) * e,
      from[2] + (to[2] - from[2]) * e
    );
  } else if (motion.kind === "circular") {
    const c = motion.center || [0, 0, 0];
    const a = (motion.phase || 0) + t * (motion.speed ?? 0.5);
    obj.position.set(
      c[0] + (motion.radius ?? 6) * Math.cos(a),
      motion.height ?? c[1] ?? 1,
      c[2] + (motion.radius ?? 6) * Math.sin(a)
    );
  }
  if (obj.userData.wheels) {
    for (const w of obj.userData.wheels) w.rotation.x = t * (motion.spin ?? 6);
  }
}

function cameraAt(cam, t) {
  if (cam.mode === "orbit") {
    const o = cam.orbit || {};
    const target = o.target || [0, 1, 0];
    const a = (o.phase || 0) + t * ((o.revolutions || 0.25) * Math.PI * 2) / Math.max(1e-6, window.__DURATION__ || 6);
    const r = o.radius ?? 14, h = o.height ?? 6;
    return { pos: [target[0] + r * Math.cos(a), h, target[2] + r * Math.sin(a)], look: target };
  }
  const keys = cam.keys || [];
  if (keys.length === 1) return { pos: keys[0].pos, look: keys[0].look };
  let i = 0;
  while (i < keys.length - 2 && t > keys[i + 1].t) i++;
  const a = keys[i], b = keys[i + 1];
  const p = Math.min(1, Math.max(0, (t - a.t) / Math.max(1e-6, b.t - a.t)));
  const e = p * p * (3 - 2 * p);
  const lerp = (u, v) => u + (v - u) * e;
  return {
    pos: [lerp(a.pos[0], b.pos[0]), lerp(a.pos[1], b.pos[1]), lerp(a.pos[2], b.pos[2])],
    look: [lerp(a.look[0], b.look[0]), lerp(a.look[1], b.look[1]), lerp(a.look[2], b.look[2])],
  };
}

function init() {
  if (renderer) return;
  const W = SPEC.shot.width, H = SPEC.shot.height;
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(W, H);
  renderer.setPixelRatio(1);
  document.getElementById("stage").appendChild(renderer.domElement);
  scene = new THREE.Scene();
  scene.background = new THREE.Color(SPEC.scene.background || "#0b1020");
  if (SPEC.scene.fog) {
    scene.fog = new THREE.Fog(SPEC.scene.fog.color || "#0b1020", SPEC.scene.fog.near ?? 30, SPEC.scene.fog.far ?? 120);
  }
  const rng = mulberry32(SPEC.seed || 0);
  void rng;
  const amb = (SPEC.scene.lights || {}).ambient || {};
  scene.add(new THREE.AmbientLight(new THREE.Color(amb.color || "#ffffff"), amb.intensity ?? 0.7));
  const dir = (SPEC.scene.lights || {}).directional || {};
  const sun = new THREE.DirectionalLight(new THREE.Color(dir.color || "#fff2df"), dir.intensity ?? 1.4);
  sun.position.set(...(dir.position || [12, 18, 8]));
  scene.add(sun);
  const g = SPEC.scene.ground || {};
  if (g.enabled !== false) {
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(g.size || 220, g.size || 220), mat(g.color || "#1c2433", 0, 0.95));
    plane.rotation.x = -Math.PI / 2;
    scene.add(plane);
    if (g.grid !== false) {
      const grid = new THREE.GridHelper(g.size || 220, Math.round((g.size || 220) / 4), 0x3a4a63, 0x2a364d);
      grid.position.y = 0.02;
      scene.add(grid);
    }
  }
  actors = [];
  for (const o of SPEC.scene.objects || []) {
    const obj = buildObject(o);
    obj.position.set(...(o.position || [0, 1, 0]));
    const rot = o.rotation || [0, 0, 0];
    obj.rotation.set(rot[0] * Math.PI / 180, rot[1] * Math.PI / 180, rot[2] * Math.PI / 180);
    scene.add(obj);
    actors.push({ obj, motion: o.motion || { kind: "static" }, baseRotY: obj.rotation.y, spin: (o.motion || {}).yaw });
  }
  camera = new THREE.PerspectiveCamera(SPEC.scene.camera.fov || 50, W / H, 0.1, 1000);
  window.__DURATION__ = SPEC.shot.duration;
}

function renderAt(t) {
  init();
  const dur = SPEC.shot.duration;
  const tt = Math.min(dur, Math.max(0, t));
  for (const a of actors) {
    applyMotion(a.obj, a.motion, tt);
    if (a.spin) a.obj.rotation.y = a.baseRotY + tt * a.spin;
  }
  const c = cameraAt(SPEC.scene.camera, tt);
  camera.position.set(...c.pos);
  camera.lookAt(...c.look);
  renderer.render(scene, camera);
}

const params = new URLSearchParams(window.location.search);
if (params.has("t")) {
  renderAt(parseFloat(params.get("t")));
  document.title = "frame@" + params.get("t");
} else {
  init();
  const clock = new THREE.Clock();
  const dur = SPEC.shot.duration;
  (function loop() {
    requestAnimationFrame(loop);
    renderAt(clock.getElapsedTime() % dur);
  })();
}
"""

_INDEX_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>__TITLE__</title>
<style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style>
</head><body><div id="stage"></div>
<script src="./scene-spec.js"></script>
<script type="module" src="./scene.js"></script>
</body></html>
"""


class ThreeJSProxy(BaseTool):
    """Render a deterministic Three.js code-video proxy + reference frame."""

    name = "threejs_proxy"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "motion_proxy"
    provider = "threejs"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL
    dependencies: list[str] = ["cmd:ffmpeg"]
    install_instructions = (
        "Scene authoring is dependency-free. Proxy rendering needs FFmpeg "
        "plus a Chrome/Chromium binary (google-chrome, chromium, "
        "/Applications/Google Chrome.app, ms-playwright cache, or CHROME_BIN). "
        "Without a renderer the build still succeeds as authoring."
    )
    agent_skills = [
        "threejs-world-generation",
        "threejs-fundamentals",
        "threejs-animation",
        "minimax-h3",
    ]
    capabilities = [
        "prompt_to_proxy_scene",
        "deterministic_proxy_render",
        "reference_frame_export",
        "editable_scene_package",
        "camera_metadata",
        "video_gen_binding_hints",
    ]
    supports = {
        "reference_to_video": True,
        "offline": True,
        "seeded": True,
        "native_audio": False,
    }
    best_for = [
        "CodeVideoModel-style motion control: deterministic 3D proxy clips that steer AI video models",
        "Editable camera trajectories (dolly/orbit/tracking) without paid generation",
        "First-frame reference stills bound into reference_to_video calls",
    ]
    not_good_for = [
        "Photoreal hero footage (the proxy is motion control, not the final look)",
        "Terrain/biome worlds (use threejs_world), character rigs, physics sims",
        "Clips longer than 15s per proxy (keep proxies short; chain in edit)",
    ]
    fallback_tools = ["threejs_world", "video_selector"]
    input_schema = {
        "type": "object",
        "required": ["operation"],
        "properties": {
            "operation": {"type": "string", "enum": ["build", "validate"]},
            "prompt": {"type": "string", "description": "Shot prompt the proxy visualizes"},
            "shot_spec": {
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "minimum": 1, "maximum": 15, "default": 6},
                    "width": {"type": "integer", "minimum": 320, "maximum": 3840, "default": 1280},
                    "height": {"type": "integer", "minimum": 240, "maximum": 2160, "default": 720},
                    "fps": {"type": "integer", "enum": [12, 24, 30], "default": 24},
                },
            },
            "scene_spec": {
                "type": "object",
                "description": "Objects, lights, ground, camera (see skill creative/code-video-proxy.md)",
                "properties": {
                    "background": {"type": "string", "default": "#0b1020"},
                    "fog": {"type": "object"},
                    "ground": {"type": "object"},
                    "lights": {"type": "object"},
                    "objects": {"type": "array"},
                    "camera": {"type": "object"},
                },
            },
            "seed": {"type": "integer", "default": 0},
            "output_path": {"type": "string", "description": "Workspace directory (required for build)"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "workspace": {"type": "string"},
            "proxy_video": {"type": ["string", "null"]},
            "reference_frame": {"type": ["string", "null"]},
            "rendered": {"type": "boolean"},
            "artifact_path": {"type": "string"},
        },
    }
    artifact_schema = {"artifact": "motion_proxy"}
    user_visible_verification = [
        "Watch the proxy clip: camera move and object motion must read clearly",
        "Check the reference frame: hero subject framed, no clipping",
    ]

    # ------------------------------------------------------------------ spec

    def _normalize(self, inputs: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []
        prompt = str(inputs.get("prompt") or "").strip()
        if not prompt:
            errors.append("prompt is required")
        elif len(prompt) > 2000:
            errors.append("prompt exceeds 2000 characters")

        shot = inputs.get("shot_spec") or {}
        duration = _number(shot.get("duration", 6), 6)
        if not 1 <= duration <= 15:
            errors.append("shot_spec.duration must be within [1, 15]")
        width = _integer(shot.get("width", 1280), 1280)
        height = _integer(shot.get("height", 720), 720)
        if not 320 <= width <= 3840 or not 240 <= height <= 2160:
            errors.append("shot_spec.width/height out of range")
        fps = _integer(shot.get("fps", 24), 24)
        if fps not in _FPS_CHOICES:
            errors.append("shot_spec.fps must be one of [12, 24, 30]")

        raw = inputs.get("scene_spec") or {}
        objects: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for index, obj in enumerate(raw.get("objects") or []):
            if not isinstance(obj, dict):
                errors.append(f"scene_spec.objects[{index}] must be an object")
                continue
            kind = obj.get("kind", "box")
            if kind not in _OBJECT_KINDS:
                errors.append(f"scene_spec.objects[{index}].kind {kind!r} unknown")
                continue
            oid = _slug(obj.get("id"), f"obj-{index}")
            if oid in seen_ids:
                errors.append(f"duplicate object id {oid!r}")
            seen_ids.add(oid)
            motion = obj.get("motion") or {"kind": "static"}
            if (motion.get("kind") or "static") not in _MOTION_KINDS:
                errors.append(f"scene_spec.objects[{index}].motion.kind unknown")
            objects.append(
                {
                    "id": oid,
                    "kind": kind,
                    "position": _vec(obj.get("position"), 3, [0, 1, 0]),
                    "rotation": _vec(obj.get("rotation"), 3, [0, 0, 0]),
                    "size": obj.get("size") or {},
                    "body": obj.get("body") or {},
                    "cabin": obj.get("cabin") or {},
                    "cabinColor": _color(obj.get("cabinColor"), "#9fb4c8"),
                    "wheelR": _number(obj.get("wheelR"), 0.4),
                    "color": _color(obj.get("color"), "#8a8f98"),
                    "metalness": min(1.0, max(0.0, _number(obj.get("metalness"), 0.1))),
                    "roughness": min(1.0, max(0.0, _number(obj.get("roughness"), 0.7))),
                    "motion": {
                        "kind": motion.get("kind") or "static",
                        "from": _vec(motion.get("from"), 3, [0, 0, 0]),
                        "to": _vec(motion.get("to"), 3, [0, 0, 0]),
                        "t0": _number(motion.get("t0"), 0),
                        "t1": _number(motion.get("t1"), duration),
                        "center": _vec(motion.get("center"), 3, [0, 1, 0]),
                        "radius": _number(motion.get("radius"), 6),
                        "height": _number(motion.get("height"), 1),
                        "speed": _number(motion.get("speed"), 0.5),
                        "phase": _number(motion.get("phase"), 0),
                        "spin": _number(motion.get("spin"), 6),
                    },
                }
            )
        if len(objects) > MAX_OBJECTS:
            errors.append(f"scene_spec.objects exceeds {MAX_OBJECTS}")
        if not objects:
            warnings.append("scene_spec.objects is empty; proxy will be camera-over-ground only")

        cam = raw.get("camera") or {}
        mode = cam.get("mode", "keys")
        if mode not in _CAMERA_MODES:
            errors.append("scene_spec.camera.mode must be 'keys' or 'orbit'")
            mode = "keys"
        keys: list[dict[str, Any]] = []
        if mode == "keys":
            for index, key in enumerate(cam.get("keys") or []):
                keys.append(
                    {
                        "t": _number((key or {}).get("t"), index),
                        "pos": _vec((key or {}).get("pos"), 3, [0, 6, 14]),
                        "look": _vec((key or {}).get("look"), 3, [0, 1, 0]),
                    }
                )
            if len(keys) < 2:
                keys = [
                    {"t": 0, "pos": [0, 6, 14], "look": [0, 1, 0]},
                    {"t": duration, "pos": [0, 6, 14], "look": [0, 1, 0]},
                ]
                warnings.append("scene_spec.camera.keys missing; using static default")
            keys = sorted(keys, key=lambda k: k["t"])[:MAX_KEYS]
            times = [k["t"] for k in keys]
            if any(b <= a for a, b in zip(times, times[1:])):
                errors.append("scene_spec.camera.keys times must be strictly increasing")
            if abs(times[0]) > 1e-6:
                errors.append("scene_spec.camera.keys must start at t=0")
            if abs(times[-1] - duration) > 1e-6:
                errors.append("scene_spec.camera.keys must end at t=duration")
        orbit = cam.get("orbit") or {}

        spec = {
            "prompt": prompt,
            "seed": _integer(inputs.get("seed"), 0),
            "shot": {"duration": duration, "width": width, "height": height, "fps": fps},
            "scene": {
                "background": _color(raw.get("background"), "#0b1020"),
                "fog": raw.get("fog"),
                "ground": raw.get("ground") or {"enabled": True},
                "lights": raw.get("lights") or {},
                "objects": objects,
                "camera": {
                    "mode": mode,
                    "fov": _number(cam.get("fov"), 50),
                    "keys": keys,
                    "orbit": {
                        "target": _vec(orbit.get("target"), 3, [0, 1, 0]),
                        "radius": _number(orbit.get("radius"), 14),
                        "height": _number(orbit.get("height"), 6),
                        "revolutions": _number(orbit.get("revolutions"), 0.25),
                        "phase": _number(orbit.get("phase"), 0),
                    },
                },
            },
        }
        return spec, errors, warnings

    # --------------------------------------------------------------- render

    def _render_frames(self, root: Path, entry: Path, frames_dir: Path, width: int, height: int, count: int, fps: int) -> tuple[bool, str]:
        chrome = _find_chrome()
        if not chrome:
            return False, "no Chrome/Chromium binary found"
        frames_dir.mkdir(parents=True, exist_ok=True)

        import http.server
        import threading

        class _Quiet(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, directory=str(root), **kwargs)

            def log_message(self, *args: Any) -> None:
                return None

        try:
            server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Quiet)
        except OSError as exc:
            return False, f"local preview server failed: {exc}"
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            def grab(index: int) -> tuple[int, str]:
                out = frames_dir / f"frame_{index:05d}.png"
                url = f"http://127.0.0.1:{port}/index.html?t={index / fps:.4f}"
                try:
                    proc = subprocess.run(
                        [
                            chrome, "--headless=new", "--hide-scrollbars",
                            # NOTE: --disable-gpu kills WebGL entirely; SwiftShader
                            # keeps software GL available for deterministic renders.
                            "--use-angle=swiftshader", "--disable-dev-shm-usage",
                            f"--window-size={width},{height}", "--timeout=20000",
                            f"--screenshot={out}", url,
                        ],
                        capture_output=True, text=True, timeout=90,
                    )
                except subprocess.TimeoutExpired:
                    return index, "timeout"
                if not out.exists() or out.stat().st_size == 0:
                    return index, (proc.stderr or "screenshot failed")[-300:]
                return index, ""

            failures: dict[int, str] = {}
            workers = min(4, max(1, count))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for index, err in pool.map(grab, range(count)):
                    if err:
                        failures[index] = err
            if failures:
                first = min(failures)
                return False, f"{len(failures)}/{count} frames failed (first @{first}: {failures[first]})"
            return True, ""
        finally:
            server.shutdown()
            thread.join()

    def _assemble(self, frames_dir: Path, out_path: Path, fps: int) -> tuple[bool, str]:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            return False, "FFmpeg not found"
        try:
            subprocess.run(
                [ffmpeg, "-y", "-framerate", str(fps), "-i", str(frames_dir / "frame_%05d.png"),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                 "-movflags", "+faststart", str(out_path)],
                capture_output=True, text=True, timeout=300, check=True,
            )
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
            return False, f"ffmpeg assembly failed: {exc}"
        return True, ""

    # -------------------------------------------------------------- execute

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        operation = str(inputs.get("operation") or "")
        if operation not in ("build", "validate"):
            return ToolResult(success=False, error="operation must be 'build' or 'validate'")
        spec, errors, warnings = self._normalize(inputs)
        if errors:
            return ToolResult(success=False, error="; ".join(errors), data={"warnings": warnings})
        if operation == "validate":
            return ToolResult(success=True, data={"spec": spec, "warnings": warnings, "rendered": False})

        output_raw = inputs.get("output_path")
        if not output_raw:
            return ToolResult(success=False, error="output_path is required for build")
        root = Path(str(output_raw))
        root.mkdir(parents=True, exist_ok=True)
        title = _slug(spec["prompt"][:48], "proxy")

        (root / "scene-spec.js").write_text(
            "window.__SCENE__ = " + json.dumps(spec) + ";\n", encoding="utf-8"
        )
        (root / "scene.js").write_text(_SCENE_JS, encoding="utf-8")
        (root / "index.html").write_text(
            _INDEX_HTML.replace("__TITLE__", f"proxy - {title}"), encoding="utf-8"
        )
        (root / "scene.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
        vendor = TEMPLATE_DIR / "three.module.min.js"
        if vendor.exists():
            shutil.copy(vendor, root / "three.module.min.js")
        else:
            warnings.append("vendored three.module.min.js missing; page needs network for CDN fallback")

        shot = spec["shot"]
        count = max(1, round(shot["duration"] * shot["fps"]))
        frames_dir = root / "frames"
        renders_dir = root / "renders"
        renders_dir.mkdir(parents=True, exist_ok=True)
        proxy_path = renders_dir / "proxy.mp4"
        frame_path = root / "reference_frame.png"

        rendered = False
        ok, msg = self._render_frames(root, root / "index.html", frames_dir, shot["width"], shot["height"], count, shot["fps"])
        if ok:
            ok, msg = self._assemble(frames_dir, proxy_path, shot["fps"])
        if ok:
            shutil.copy(frames_dir / "frame_00000.png", frame_path)
            rendered = True
        else:
            warnings.append(
                "proxy render skipped/failed (" + msg + "); render later via "
                "video_compose/hyperframes_compose on this workspace"
            )

        cam = spec["scene"]["camera"]
        artifact = {
            "version": "1.0",
            "prompt": spec["prompt"],
            "seed": spec["seed"],
            "duration_seconds": shot["duration"],
            "fps": shot["fps"],
            "width": shot["width"],
            "height": shot["height"],
            "proxy_video": str(proxy_path) if rendered else None,
            "reference_frame": str(frame_path) if rendered else None,
            "scene_package": {
                "workspace": str(root),
                "entry": str(root / "index.html"),
                "spec": str(root / "scene.json"),
            },
            "camera": {"mode": cam["mode"], "key_count": len(cam.get("keys") or [])},
            "object_count": len(spec["scene"]["objects"]),
            "rendered": rendered,
            "provider_hints": {
                "suggested_operation": "reference_to_video",
                "reference_video_paths": [str(proxy_path)] if rendered else [],
                "reference_image_paths": [str(frame_path)] if rendered else [],
                "prompt_note": "Cite proxy as motion/structure control (Video 1) and the still as look lock (Image 1).",
            },
            "warnings": warnings,
        }
        try:
            from schemas.artifacts import validate_artifact

            validate_artifact("motion_proxy", artifact)
        except Exception as exc:  # contract violation must fail fast
            return ToolResult(success=False, error=f"motion_proxy artifact invalid: {exc}")
        artifact_path = root / "motion_proxy.json"
        artifact_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        return ToolResult(
            success=True,
            data={
                "workspace": str(root),
                "proxy_video": str(proxy_path) if rendered else None,
                "reference_frame": str(frame_path) if rendered else None,
                "rendered": rendered,
                "artifact_path": str(artifact_path),
                "duration_seconds": shot["duration"],
                "fps": shot["fps"],
                "seed": spec["seed"],
                "warnings": warnings,
            },
            artifacts=[str(artifact_path)],
            seed=spec["seed"],
        )
