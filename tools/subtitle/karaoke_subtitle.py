"""Karaoke subtitle tool for OpenMontage — word-by-word color + pop.

Generates an ASS subtitle with karaoke timing so words are **colored
progressively as they are spoken** (PrimaryColour -> SecondaryColour via `{\\k}`
tags), plus a gentle font **pop** (slightly larger highlight + scale pulse).

Timing comes from faster-whisper word timestamps; the displayed TEXT is the
accurate scripture/script (대본), with word timestamps mapped by proportional
alignment. Run with the `ass=` filter in compositing.

Usage:  python tools/subtitle/karaoke_subtitle.py --audio narration.wav \
          --script "line1" "line2" --output out.ass
"""

from __future__ import annotations

import argparse
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

FONT = "NanumGothic"
PRIMARY = "&H00FFFFFF"       # white (unspoken base)
HIGHLIGHT = "&H008CD0F5"     # amber #F5D08C (ASS BBGGRR) — spoken word highlight


def _split_words(text: str) -> list[str]:
    import re
    words = re.findall(r"\S+", text)
    return words or [text.strip()]


def _map_word_times(words: list[str], total_start: float, total_end: float) -> list[tuple[float, float]]:
    """Distribute a segment's time across its words proportionally (by char length)."""
    if not words:
        return []
    lens = [max(1, len(w)) for w in words]
    total = sum(lens)
    dur = max(0.0, total_end - total_start)
    out = []
    t = total_start
    for l in lens:
        w_dur = dur * l / total
        out.append((t, t + w_dur))
        t += w_dur
    return out


def build_ass(segments, script_lines: list[str], play_w: int = 1280, play_h: int = 720) -> str:
    """Assemble an ASS with karaoke coloring + per-word pop.

    Resolution-aware: font, margins scale with play_h so the base karaoke line
    sits near the bottom and the pop word floats ABOVE it (no overlap).
    """
    fs = max(16, round(play_h * 0.034))         # base font
    base_margin = max(24, round(play_h * 0.10))  # base line near bottom
    pop_margin = base_margin + round(fs * 2.6)   # pop word above the line

    events = []
    for i, seg in enumerate(segments):
        seg_start = seg["start"]
        seg_end = seg["end"]
        line = script_lines[i] if i < len(script_lines) else seg["text"]
        words = _split_words(line)
        times = _map_word_times(words, seg_start, seg_end)

        kara = []
        for (w, (t0, t1)) in zip(words, times):
            centi = max(1, int(round((t1 - t0) * 100)))
            kara.append(f"{{\\k{centi}}}{w} ")
        events.append(
            f"Dialogue: 0,{_fmt_ass(seg_start)},{_fmt_ass(seg_end)},Default,,0,0,0,,{''.join(kara).strip()}"
        )

        # Per-word pop layer (larger, bold, above the line)
        for (w, (t0, t1)) in zip(words, times):
            pop_txt = f"{{\\fscx110\\fscy110}}{w}"
            events.append(
                f"Dialogue: 1,{_fmt_ass(t0)},{_fmt_ass(t1)},Pop,,0,0,0,,{pop_txt}"
            )

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_w}
PlayResY: {play_h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT},{fs},&H00FFFFFF,{HIGHLIGHT},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,{base_margin},1
Style: Pop,{FONT},{fs},{HIGHLIGHT},&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,{pop_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return header + "\n".join(events) + "\n"


def _fmt_ass(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds % 1) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


class KaraokeSubtitle(BaseTool):
    name = "karaoke_subtitle"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "subtitle"
    provider = "faster-whisper"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "Requires faster-whisper (offline) for word timestamps."
    agent_skills = ["speech-to-text"]

    capabilities = ["karaoke_subtitle", "word_highlight", "ass_generation"]

    input_schema = {
        "type": "object",
        "required": ["audio_path"],
        "properties": {
            "audio_path": {"type": "string"},
            "output_path": {"type": "string"},
            "script_lines": {"type": "array", "items": {"type": "string"}},
            "model_size": {"type": "string", "default": "small"},
            "language": {"type": "string", "default": "ko"},
            "play_w": {"type": "integer", "default": 1280},
            "play_h": {"type": "integer", "default": 720},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=2048, vram_mb=0, disk_mb=200)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["audio_path"]
    side_effects = ["writes .ass to output_path"]
    user_visible_verification = [
        "Words color progressively as spoken (karaoke highlight)",
        "Highlight font pops slightly larger than the base line",
    ]

    def get_status(self) -> ToolStatus:
        try:
            from tools.analysis.transcriber import Transcriber  # noqa: F401
            return ToolStatus.AVAILABLE
        except Exception:
            return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 15.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        audio = Path(inputs.get("audio_path", "")).resolve()
        if not audio.is_file():
            return ToolResult(success=False, error="audio_path required")
        out = Path(inputs.get("output_path", str(audio.with_suffix(".ass")))).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        from tools.analysis.transcriber import Transcriber
        r = Transcriber().execute({
            "input_path": str(audio),
            "model_size": inputs.get("model_size", "small"),
            "language": inputs.get("language", "ko"),
        })
        if not r.success:
            return ToolResult(success=False, error=f"transcription failed: {r.error}")
        segments = r.data.get("segments", [])
        if not segments:
            return ToolResult(success=False, error="no segments")

        script = inputs.get("script_lines") or []
        play_w = int(inputs.get("play_w", 1280))
        play_h = int(inputs.get("play_h", 720))
        ass = build_ass(segments, script, play_w, play_h)
        out.write_text(ass, encoding="utf-8")

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(out),
                  "segments": len(segments), "words_colored": sum(len(_split_words(s["text"])) for s in segments)},
            artifacts=[str(out)], duration_seconds=round(time.time() - start, 2),
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--script", nargs="*", default=[])
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    args = ap.parse_args()
    res = KaraokeSubtitle().execute({
        "audio_path": args.audio, "output_path": args.output, "script_lines": args.script,
        "play_w": args.width, "play_h": args.height})
    print(res.success, res.data if res.success else res.error)
