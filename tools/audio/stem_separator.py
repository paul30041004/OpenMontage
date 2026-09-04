"""Demucs stem separation tool — vocals, drums, bass, other.

Uses Meta's Demucs v4 (htdemucs) to split a music track into isolated
stems. Powers the viral X/Threads workflows: vocal-removed instrumentals,
a cappella extraction, and remix stems — fully local on CPU / MPS.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    DependencyError,
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


class StemSeparator(BaseTool):
    name = "stem_separator"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "audio_processing"
    provider = "demucs"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:demucs"]
    install_instructions = (
        "Install Demucs:\n"
        "  pip install demucs\n"
        "First run downloads the htdemucs model (~320MB) into ~/.cache/torch."
    )
    agent_skills = ["elevenlabs", "music"]

    capabilities = [
        "stem_separation",
        "vocal_isolation",
        "instrumental_extraction",
        "music_remix",
    ]
    supports = {
        "stems": ["vocals", "drums", "bass", "other"],
        "offline": True,
        "mps": True,
    }
    best_for = [
        "vocal-removed instrumentals for background music",
        "a cappella / vocal stems for remixes",
        "drum and bass stems for mashups",
    ]
    not_good_for = [
        "speech source separation (use audio_enhance instead)",
        "real-time separation",
    ]

    input_schema = {
        "type": "object",
        "required": ["input_path"],
        "properties": {
            "input_path": {"type": "string"},
            "output_dir": {"type": "string"},
            "stems": {
                "type": "array",
                "items": {"type": "string", "enum": ["vocals", "drums", "bass", "other"]},
                "default": ["vocals", "drums", "bass", "other"],
                "description": "Which stems to write out. Empty = all.",
            },
            "two_stems": {
                "type": "string",
                "enum": ["vocals", "drums", "bass", "other"],
                "description": "Split into just two stems: this one and 'no_<stem>' (faster, less memory).",
            },
            "model": {
                "type": "string",
                "enum": ["htdemucs", "htdemucs_ft", "htdemucs_6s", "mdx_extra"],
                "default": "htdemucs",
            },
            "segment": {
                "type": "number",
                "default": 7,
                "description": "Segment length in seconds (higher = better quality, more memory)",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=4096, vram_mb=0, disk_mb=1000, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["input_path", "stems", "model", "segment"]
    side_effects = [
        "writes stem wav files to output_dir",
        "downloads model to ~/.cache/torch on first run",
    ]
    user_visible_verification = [
        "Listen to the vocal stem — should contain only the voice",
    ]

    def get_status(self) -> ToolStatus:
        try:
            import demucs  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        try:
            import demucs  # noqa: F401
        except ImportError as exc:
            raise DependencyError(
                f"Python module 'demucs' not installed. {self.install_instructions}"
            ) from exc

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        if self.get_status() != ToolStatus.AVAILABLE:
            return ToolResult(
                success=False,
                error="Demucs not available. " + self.install_instructions,
            )

        start = time.time()
        try:
            result = self._separate(inputs)
        except Exception as exc:
            return ToolResult(success=False, error=f"Stem separation failed: {exc}")

        result.duration_seconds = round(time.time() - start, 2)
        return result

    def _separate(self, inputs: dict[str, Any]) -> ToolResult:
        import demucs.separate
        import sys
        from io import StringIO

        input_path = Path(inputs["input_path"]).expanduser()
        if not input_path.is_file():
            return ToolResult(success=False, error=f"Input file not found: {input_path}")

        # Demucs writes stems next to the input by default; route to output_dir.
        output_dir = inputs.get("output_dir") or str(input_path.parent)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        two_stems = inputs.get("two_stems")
        model = inputs.get("model", "htdemucs")

        args = [
            "-n", model,
            "-o", output_dir,
            "--segment", str(int(inputs.get("segment", 7))),
        ]
        if two_stems:
            args += ["--two-stems", two_stems]
        else:
            args += ["--stems", ",".join(inputs.get("stems", ["vocals", "drums", "bass", "other"]))]
        args.append(str(input_path))

        # Capture demucs console output (it prints progress to stdout).
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            demucs.separate.main(args)
        finally:
            sys.stdout = old_stdout

        track_dir = Path(output_dir) / model / (input_path.stem + "_" + model)
        if not track_dir.is_dir():
            # Some versions nest differently; search recursively.
            matches = list(Path(output_dir).rglob("*.wav"))
            if not matches:
                return ToolResult(
                    success=False,
                    error=f"Demucs produced no stems in {output_dir}",
                )
        else:
            matches = sorted(track_dir.glob("*.wav"))

        stems = {}
        for wav in matches:
            stems[wav.stem] = str(wav)

        if not stems:
            return ToolResult(success=False, error="Demucs produced no stem files")

        return ToolResult(
            success=True,
            data={
                "provider": self.provider,
                "model": model,
                "stems": stems,
                "output_dir": str(track_dir if track_dir.is_dir() else output_dir),
            },
            artifacts=list(stems.values()),
            model=model,
        )
