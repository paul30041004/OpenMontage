"""App benchmarking dossier tool.

Turns an app tutorial video into a feature-evidence dossier, links each
observed feature to a REA (reverse-engineering MCP) investigation plan, stores
the findings the agent brings back, and renders a gap report that drives
"do it better than the original" feature design.

Python here is scaffolding + persistence only. Which features exist, what the
REA evidence means, and which improvements to pursue are the agent's judgement
(see skills/meta/app-benchmarking.md). REA itself is an MCP server: this tool
produces the call plan and ingests results, it never calls REA directly.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolTier,
)

DOSSIER_NAME = "benchmark_dossier.json"
REPORT_NAME = "benchmark_report.md"

# target kind -> ordered REA MCP calls that answer "how is this feature built?"
REA_PLANS: dict[str, list[dict[str, str]]] = {
    "web": [
        {"tool": "capture_browser_scenario", "why": "replay the tutorial steps and capture network/DOM"},
        {"tool": "inspect_web_network_capture", "why": "find the API calls behind the feature"},
        {"tool": "analyze_web_bundle", "why": "locate feature modules in the shipped bundle"},
        {"tool": "trace_web_source_location", "why": "map UI element to source module"},
    ],
    "electron": [
        {"tool": "capture_electron_scenario", "why": "replay the tutorial steps against the app"},
        {"tool": "analyze_javascript_application", "why": "map renderer/main modules"},
        {"tool": "trace_application_feature", "why": "trace the feature from UI to logic"},
        {"tool": "inspect_electron_fuses", "why": "note hardening limits on analysis"},
    ],
    "android": [
        {"tool": "inspect_android_package", "why": "permissions, components, SDKs"},
        {"tool": "search_android_classes", "why": "find classes named after the feature"},
        {"tool": "trace_android_references", "why": "follow callers from UI to logic"},
        {"tool": "capture_adb_screen", "why": "compare live screens with tutorial frames"},
    ],
    "apple": [
        {"tool": "inspect_macho", "why": "linked frameworks hint at capabilities"},
        {"tool": "project_apple_application_graph", "why": "app-level component graph"},
        {"tool": "trace_application_feature", "why": "trace the feature from UI to logic"},
        {"tool": "capture_native_ui_scenario", "why": "replay tutorial steps and compare screens"},
    ],
    "native": [
        {"tool": "binary_overview", "why": "format, imports, strings overview"},
        {"tool": "search_strings", "why": "find UI labels seen in the tutorial"},
        {"tool": "trace_feature", "why": "trace the feature through procedures"},
        {"tool": "procedure_pseudo_code", "why": "read the decompiled core routine"},
    ],
    "managed": [
        {"tool": "inspect_managed_artifact", "why": "assemblies/types overview"},
        {"tool": "project_managed_application_graph", "why": "app-level component graph"},
        {"tool": "inspect_managed_members", "why": "read members behind the feature"},
    ],
}

FEATURE_STATUSES = ("observed", "traced", "unverifiable")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _load(workdir: Path) -> dict[str, Any]:
    path = workdir / DOSSIER_NAME
    if not path.is_file():
        raise FileNotFoundError(f"No dossier at {path}; run operation 'init' first")
    return json.loads(path.read_text(encoding="utf-8"))


def _save(workdir: Path, dossier: dict[str, Any]) -> Path:
    dossier["updated_at"] = _now()
    path = workdir / DOSSIER_NAME
    path.write_text(json.dumps(dossier, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _slug(name: str) -> str:
    slug = re.sub(r"[^\w]+", "-", name.strip().lower(), flags=re.UNICODE).strip("-")
    return slug or "feature"


def parse_srt(text: str) -> list[dict[str, Any]]:
    """Parse SRT text into [{start, end, text}] (seconds)."""
    segments = []
    pattern = re.compile(
        r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*?)(?:\n\s*\n|\Z)",
        re.S,
    )
    for m in pattern.finditer(text.replace("\r\n", "\n")):
        h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(m.group(i)) for i in range(1, 9))
        segments.append({
            "start": h1 * 3600 + m1 * 60 + s1 + ms1 / 1000,
            "end": h2 * 3600 + m2 * 60 + s2 + ms2 / 1000,
            "text": " ".join(m.group(9).split()),
        })
    return dedupe_rolling(segments)


def dedupe_rolling(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse YouTube auto-caption cues that repeat the previous cue's text.

    Auto captions roll: each cue holds the previous line plus new words, and
    short filler cues repeat the tail. Keep only the newly added words.
    """
    out: list[dict[str, Any]] = []
    prev = ""
    for seg in segments:
        text = seg["text"]
        if not text or seg["end"] - seg["start"] < 0.1:
            continue
        if prev and text == prev:
            continue
        if prev and prev in text:
            tail = text.split(prev, 1)[1].strip() if text.startswith(prev) else text
        elif prev and text in prev:
            continue
        else:
            tail = text
        if tail:
            out.append({"start": seg["start"], "end": seg["end"], "text": tail})
        prev = text
    return out


def nearest_items(items: list[dict], key: str, ts: float, limit: int = 2) -> list[dict]:
    return sorted(items, key=lambda i: abs(i[key] - ts))[:limit]


class AppBenchmark(BaseTool):
    name = "app_benchmark"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "analysis"
    provider = "local"
    stability = ToolStability.EXPERIMENTAL
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg", "cmd:ffprobe"]
    install_instructions = "Install FFmpeg: https://ffmpeg.org/download.html"
    agent_skills = ["ffmpeg"]

    capabilities = [
        "ingest_tutorial_video",
        "feature_evidence_dossier",
        "rea_investigation_plan",
        "gap_report",
    ]

    input_schema = {
        "type": "object",
        "required": ["operation", "workdir"],
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "init", "ingest_video", "add_feature", "rea_plan",
                    "record_findings", "gap_report",
                ],
            },
            "workdir": {"type": "string", "description": "Benchmark project directory"},
            "app_name": {"type": "string", "description": "init: app being benchmarked"},
            "target_kind": {
                "type": "string",
                "enum": sorted(REA_PLANS),
                "description": "init: how the app ships, selects the REA plan",
            },
            "target_path": {
                "type": "string",
                "description": "init: binary/apk/app bundle path or URL REA will open",
            },
            "video_path": {"type": "string", "description": "ingest_video: tutorial video"},
            "srt_path": {"type": "string", "description": "ingest_video: optional transcript"},
            "scene_threshold": {"type": "number", "default": 0.3},
            "max_frames": {"type": "integer", "default": 60},
            "max_gap_seconds": {"type": "number", "default": 12.0},
            "feature_name": {"type": "string"},
            "timestamps": {"type": "array", "items": {"type": "number"}},
            "ui_notes": {"type": "string", "description": "add_feature: what the frames show"},
            "limitations": {"type": "array", "items": {"type": "string"}},
            "improvement_ideas": {"type": "array", "items": {"type": "string"}},
            "status": {"type": "string", "enum": list(FEATURE_STATUSES)},
            "rea_tool": {"type": "string", "description": "record_findings: REA tool used"},
            "summary": {"type": "string", "description": "record_findings: what REA showed"},
            "evidence_refs": {"type": "array", "items": {"type": "string"}},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=512, disk_mb=500)
    side_effects = ["writes frames, benchmark_dossier.json and benchmark_report.md to workdir"]
    user_visible_verification = ["Check each feature's frames match what the tutorial narrates"]

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        op = inputs["operation"]
        workdir = Path(inputs["workdir"])
        start = time.time()
        try:
            handler = getattr(self, f"_op_{op}")
            data, artifacts = handler(workdir, inputs)
        except (FileNotFoundError, ValueError, KeyError) as e:
            return ToolResult(success=False, error=str(e))
        except Exception as e:  # ffmpeg failures etc.
            return ToolResult(success=False, error=f"{op} failed: {e}")
        return ToolResult(
            success=True, data=data, artifacts=artifacts,
            duration_seconds=round(time.time() - start, 2),
        )

    # -- operations ---------------------------------------------------------

    def _op_init(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        kind = inputs.get("target_kind")
        if kind and kind not in REA_PLANS:
            raise ValueError(f"target_kind must be one of {sorted(REA_PLANS)}")
        if not inputs.get("app_name"):
            raise ValueError("init requires app_name")
        workdir.mkdir(parents=True, exist_ok=True)
        path = workdir / DOSSIER_NAME
        if path.exists():
            raise ValueError(f"Dossier already exists: {path}")
        dossier = {
            "app_name": inputs["app_name"],
            "target": {"kind": kind, "path": inputs.get("target_path")},
            "created_at": _now(),
            "video": None,
            "frames": [],
            "transcript": [],
            "features": [],
        }
        _save(workdir, dossier)
        return {"dossier": str(path)}, [str(path)]

    def _op_ingest_video(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        dossier = _load(workdir)
        video = Path(inputs.get("video_path", ""))
        if not video.is_file():
            raise FileNotFoundError(f"Video not found: {video}")
        threshold = inputs.get("scene_threshold", 0.3)
        max_frames = inputs.get("max_frames", 60)
        duration = self._duration(video)
        times = self._scene_times(video, threshold)
        times = self._fill_gaps(sorted({0.1, *times}), duration, inputs.get("max_gap_seconds", 12.0))
        if len(times) > max_frames:
            step = len(times) / max_frames
            times = [times[int(i * step)] for i in range(max_frames)]

        frames_dir = workdir / "frames"
        frames_dir.mkdir(exist_ok=True)
        frames = []
        for i, ts in enumerate(times):
            out = frames_dir / f"frame_{i:04d}.jpg"
            self.run_command([
                "ffmpeg", "-y", "-ss", str(ts), "-i", str(video),
                "-frames:v", "1", "-qscale:v", "2", str(out),
            ])
            if out.exists():
                frames.append({"path": str(out), "t": round(ts, 3)})

        transcript = []
        srt = inputs.get("srt_path")
        if srt:
            transcript = parse_srt(Path(srt).read_text(encoding="utf-8", errors="ignore"))

        dossier["video"] = {"path": str(video), "duration_seconds": duration}
        dossier["frames"] = frames
        dossier["transcript"] = transcript
        path = _save(workdir, dossier)
        return (
            {"duration_seconds": duration, "frame_count": len(frames),
             "transcript_segments": len(transcript)},
            [str(frames_dir), str(path)],
        )

    def _op_add_feature(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        dossier = _load(workdir)
        name = inputs.get("feature_name")
        stamps = inputs.get("timestamps") or []
        if not name or not stamps:
            raise ValueError("add_feature requires feature_name and timestamps")
        if not dossier["frames"]:
            raise ValueError("Run ingest_video before add_feature")
        fid = _slug(name)
        if any(f["id"] == fid for f in dossier["features"]):
            raise ValueError(f"Feature already recorded: {fid}")
        frames, lines = [], []
        for ts in stamps:
            frames += [f["path"] for f in nearest_items(dossier["frames"], "t", ts)]
            if dossier["transcript"]:
                lines += [s["text"] for s in nearest_items(dossier["transcript"], "start", ts, 1)]
        dossier["features"].append({
            "id": fid,
            "name": name,
            "status": "observed",
            "timestamps": stamps,
            "frames": list(dict.fromkeys(frames)),
            "narration": list(dict.fromkeys(lines)),
            "ui_notes": inputs.get("ui_notes", ""),
            "limitations": inputs.get("limitations", []),
            "improvement_ideas": inputs.get("improvement_ideas", []),
            "rea_findings": [],
        })
        path = _save(workdir, dossier)
        return {"feature_id": fid, "feature_count": len(dossier["features"])}, [str(path)]

    def _op_rea_plan(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        dossier = _load(workdir)
        target = dossier["target"]
        if not target.get("kind"):
            raise ValueError("Dossier has no target_kind; cannot choose a REA plan")
        steps = REA_PLANS[target["kind"]]
        plan = [
            {
                "feature_id": f["id"],
                "feature": f["name"],
                "ui_hint": f["ui_notes"],
                "target": target["path"],
                "calls": steps,
            }
            for f in dossier["features"]
            if f["status"] == "observed"
        ]
        return {"target": target, "plan": plan}, []

    def _op_record_findings(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        dossier = _load(workdir)
        fid = _slug(inputs.get("feature_name", ""))
        feature = next((f for f in dossier["features"] if f["id"] == fid), None)
        if feature is None:
            raise KeyError(f"Unknown feature: {fid}")
        if not inputs.get("summary") or not inputs.get("rea_tool"):
            raise ValueError("record_findings requires rea_tool and summary")
        status = inputs.get("status", "traced")
        if status not in FEATURE_STATUSES:
            raise ValueError(f"status must be one of {FEATURE_STATUSES}")
        feature["rea_findings"].append({
            "tool": inputs["rea_tool"],
            "summary": inputs["summary"],
            "evidence_refs": inputs.get("evidence_refs", []),
            "at": _now(),
        })
        feature["status"] = status
        for key in ("limitations", "improvement_ideas"):
            feature[key] = list(dict.fromkeys(feature[key] + inputs.get(key, [])))
        path = _save(workdir, dossier)
        return {"feature_id": fid, "status": status}, [str(path)]

    def _op_gap_report(self, workdir: Path, inputs: dict) -> tuple[dict, list[str]]:
        dossier = _load(workdir)
        features = dossier["features"]
        lines = [
            f"# Benchmark: {dossier['app_name']}",
            "",
            "| Feature | Status | REA evidence | Limitations | Improvements |",
            "| --- | --- | --- | --- | --- |",
        ]
        for f in features:
            lines.append(
                f"| {f['name']} | {f['status']} | {len(f['rea_findings'])} | "
                f"{len(f['limitations'])} | {len(f['improvement_ideas'])} |"
            )
        for f in features:
            lines += ["", f"## {f['name']} (`{f['status']}`)"]
            if f["timestamps"]:
                lines.append("Seen at: " + ", ".join(f"{t:.1f}s" for t in f["timestamps"]))
            if f["narration"]:
                lines += ["", "Narration:"] + [f"- {n}" for n in f["narration"]]
            if f["ui_notes"]:
                lines += ["", f"UI: {f['ui_notes']}"]
            if f["rea_findings"]:
                lines += ["", "REA findings:"]
                lines += [f"- [{r['tool']}] {r['summary']}" for r in f["rea_findings"]]
            if f["limitations"]:
                lines += ["", "Weaknesses:"] + [f"- {x}" for x in f["limitations"]]
            if f["improvement_ideas"]:
                lines += ["", "Beat-it ideas:"] + [f"- {x}" for x in f["improvement_ideas"]]
        needs_evidence = [f["id"] for f in features if not f["rea_findings"]]
        needs_ideas = [f["id"] for f in features if not f["improvement_ideas"]]
        report = workdir / REPORT_NAME
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return (
            {"report": str(report), "features_without_rea_evidence": needs_evidence,
             "features_without_improvements": needs_ideas},
            [str(report)],
        )

    # -- ffmpeg helpers -----------------------------------------------------

    def _duration(self, video: Path) -> float:
        result = self.run_command([
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "json", str(video),
        ])
        return float(json.loads(result.stdout).get("format", {}).get("duration", 0))

    @staticmethod
    def _fill_gaps(times: list[float], duration: float, max_gap: float) -> list[float]:
        """Screen recordings change gradually; guarantee no stretch longer than max_gap goes unseen."""
        filled = [times[0]]
        for t in times[1:] + [max(duration - 0.5, times[-1])]:
            gap = t - filled[-1]
            if gap > max_gap:
                n = int(gap // max_gap)
                step = gap / (n + 1)
                filled += [filled[-1] + step * (k + 1) for k in range(n)]
            if t != filled[-1]:
                filled.append(t)
        return sorted(set(round(t, 3) for t in filled))

    def _scene_times(self, video: Path, threshold: float) -> list[float]:
        result = self.run_command([
            "ffmpeg", "-i", str(video),
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-an", "-f", "null", "-",
        ])
        text = (result.stderr or "") + (result.stdout or "")
        return [float(t) for t in re.findall(r"pts_time:([0-9.]+)", text)]
