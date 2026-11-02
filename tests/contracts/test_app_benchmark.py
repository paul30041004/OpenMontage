"""Contracts for the app benchmarking dossier tool."""

import shutil
import subprocess
from pathlib import Path

import pytest

from tools.analysis.app_benchmark import AppBenchmark, parse_srt

SRT = """1
00:00:01,000 --> 00:00:03,000
Click the export button.

2
00:00:05,500 --> 00:00:07,000
Now choose a template.
"""

needs_ffmpeg = pytest.mark.skipif(
    not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="ffmpeg missing"
)


def test_parse_srt() -> None:
    segs = parse_srt(SRT)
    assert [s["text"] for s in segs] == ["Click the export button.", "Now choose a template."]
    assert segs[1]["start"] == 5.5


def _run(tool: AppBenchmark, **kw):
    result = tool.execute(kw)
    assert result.success, result.error
    return result


def test_flow_without_video_errors_cleanly(tmp_path: Path) -> None:
    tool = AppBenchmark()
    _run(tool, operation="init", workdir=str(tmp_path), app_name="Demo", target_kind="web")
    dup = tool.execute({"operation": "init", "workdir": str(tmp_path), "app_name": "Demo"})
    assert not dup.success
    r = tool.execute({"operation": "add_feature", "workdir": str(tmp_path),
                      "feature_name": "Export", "timestamps": [1]})
    assert not r.success and "ingest_video" in r.error


def test_rea_plan_requires_target_kind(tmp_path: Path) -> None:
    tool = AppBenchmark()
    _run(tool, operation="init", workdir=str(tmp_path), app_name="Demo")
    assert not tool.execute({"operation": "rea_plan", "workdir": str(tmp_path)}).success


@needs_ffmpeg
def test_full_flow(tmp_path: Path) -> None:
    video = tmp_path / "tut.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=red:s=160x120:d=2",
         "-f", "lavfi", "-i", "color=blue:s=160x120:d=2",
         "-filter_complex", "[0][1]concat=n=2:v=1:a=0", str(video)],
        check=True, capture_output=True,
    )
    srt = tmp_path / "tut.srt"
    srt.write_text(SRT, encoding="utf-8")
    work = tmp_path / "bench"
    tool = AppBenchmark()
    _run(tool, operation="init", workdir=str(work), app_name="Demo",
         target_kind="electron", target_path="/Applications/Demo.app")
    ing = _run(tool, operation="ingest_video", workdir=str(work),
               video_path=str(video), srt_path=str(srt))
    assert ing.data["frame_count"] >= 2 and ing.data["transcript_segments"] == 2

    _run(tool, operation="add_feature", workdir=str(work), feature_name="Export",
         timestamps=[1.0], ui_notes="Export button top right")
    plan = _run(tool, operation="rea_plan", workdir=str(work)).data["plan"]
    assert plan[0]["feature_id"] == "export"
    assert plan[0]["calls"][0]["tool"] == "capture_electron_scenario"

    gap = _run(tool, operation="gap_report", workdir=str(work)).data
    assert gap["features_without_rea_evidence"] == ["export"]

    _run(tool, operation="record_findings", workdir=str(work), feature_name="Export",
         rea_tool="trace_application_feature", summary="Calls /api/export, PNG only",
         limitations=["PNG only"], improvement_ideas=["Add SVG/PDF export"])
    gap = _run(tool, operation="gap_report", workdir=str(work)).data
    assert gap["features_without_rea_evidence"] == []
    assert gap["features_without_improvements"] == []
    assert "Add SVG/PDF export" in Path(gap["report"]).read_text(encoding="utf-8")
