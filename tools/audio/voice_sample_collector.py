"""Voice sample collector — harvest natural human voice clips from SNS videos.

Downloads audio from YouTube / Shorts / Instagram / TikTok (via yt-dlp CLI),
detects continuous speech regions (via FFmpeg silencedetect), and cuts them
into 15-20 second MP3 clips. These clips become the anchor/reference samples
that power higher-quality, more human-sounding TTS (VoxCPM / Fish S2-Pro /
Bert-VITS2 voice cloning).

The goal is a growing library of attractive, natural, real-human voice samples
for TTS quality improvement and voice-clone training.

Output layout (under output_dir, default `voice_samples/`):
    voice_samples/
    ├── <video_id>_0001.mp3
    ├── <video_id>_0002.mp3
    └── manifest.json          # provenance: source URL, title, uploader, timestamps
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
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

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "voice_samples"


class VoiceSampleCollector(BaseTool):
    name = "voice_sample_collector"
    version = "1.0.0"
    tier = ToolTier.SOURCE
    capability = "training"
    provider = "openmontage"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:yt-dlp", "cmd:ffmpeg", "cmd:ffprobe"]
    install_instructions = (
        "Requires yt-dlp and FFmpeg on PATH.\n"
        "  brew install yt-dlp ffmpeg\n"
        "Optional (for speech verification): brew install whisper-cpp"
    )
    agent_skills = ["video-download", "ffmpeg", "speech-to-text"]

    capabilities = [
        "voice_sample_collection",
        "speech_segment_detection",
        "audio_clip_cutting",
        "tts_training_corpus",
    ]

    supports = {
        "youtube": True,
        "shorts": True,
        "instagram": True,
        "tiktok": True,
        "offline_cutting": True,
        "silence_detection": True,
    }

    best_for = [
        "harvesting natural human voice samples for TTS quality improvement",
        "building a voice-clone reference corpus from real SNS videos",
        "collecting attractive, natural-sounding anchor samples",
    ]
    not_good_for = [
        "music-only or instrumental content",
        "DRM-protected or paywalled media",
    ]

    input_schema = {
        "type": "object",
        "required": ["url"],
        "properties": {
            "url": {
                "type": "string",
                "description": "Video URL (YouTube, Shorts, Instagram, TikTok, etc.).",
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to store collected MP3 clips and manifest. Defaults to voice_samples/.",
            },
            "segment_duration": {
                "type": "number",
                "default": 15.0,
                "minimum": 10.0,
                "maximum": 20.0,
                "description": "Target clip length in seconds (15-20s recommended for TTS anchors).",
            },
            "max_segments": {
                "type": "integer",
                "default": 8,
                "minimum": 1,
                "maximum": 50,
                "description": "Maximum number of clips to cut from one video.",
            },
            "silence_threshold_db": {
                "type": "number",
                "default": -35,
                "description": "Audio level below this (dB) is treated as silence.",
            },
            "min_speech_gap": {
                "type": "number",
                "default": 0.6,
                "description": "Gap (seconds) between speech bursts that still counts as continuous speech.",
            },
            "language": {
                "type": "string",
                "description": "Optional ISO language code (ko/en/ja/zh) for metadata tagging.",
            },
        },
    }

    output_schema = {
        "type": "object",
        "properties": {
            "clips": {"type": "array", "items": {"type": "string"}},
            "manifest_path": {"type": "string"},
            "source_title": {"type": "string"},
            "source_uploader": {"type": "string"},
            "clip_count": {"type": "integer"},
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=2000, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["download"])
    side_effects = ["downloads audio from URL", "writes MP3 clips and manifest.json"]
    user_visible_verification = [
        "Listen to clips: they should be clean, continuous human speech (no music/silence)",
        "Verify clips are 15-20s and contain a single consistent speaker",
    ]

    def get_status(self) -> ToolStatus:
        if shutil.which("yt-dlp") and shutil.which("ffmpeg") and shutil.which("ffprobe"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 60.0

    # ------------------------------------------------------------------ #
    # Execution
    # ------------------------------------------------------------------ #
    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        url = inputs["url"].strip()
        if not url:
            return ToolResult(success=False, error="url is required")

        output_dir = Path(inputs.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
        output_dir.mkdir(parents=True, exist_ok=True)

        segment_duration = float(inputs.get("segment_duration", 15.0))
        max_segments = int(inputs.get("max_segments", 8))
        silence_db = float(inputs.get("silence_threshold_db", -35))
        min_gap = float(inputs.get("min_speech_gap", 0.6))
        language = inputs.get("language")

        start = time.time()

        # 1. Download audio
        audio_path, meta = self._download_audio(url, output_dir)
        if audio_path is None:
            return ToolResult(
                success=False,
                error=f"Audio download failed: {meta.get('error', 'unknown error')}",
                data={"metadata": meta},
            )

        # 2. Detect speech segments
        speech_segments = self._detect_speech(audio_path, silence_db, min_gap)
        if not speech_segments:
            return ToolResult(
                success=False,
                error="No continuous speech detected in this video (may be music-only or silent).",
                data={"metadata": meta},
            )

        # 3. Build 15-20s windows from speech segments
        windows = self._build_windows(speech_segments, segment_duration, max_segments)

        # 4. Cut clips
        video_id = meta.get("id", "clip")
        clips = []
        for i, (w_start, w_end) in enumerate(windows, 1):
            clip_path = output_dir / f"{video_id}_{i:04d}.mp3"
            ok = self._cut_clip(audio_path, clip_path, w_start, w_end)
            if ok:
                clips.append(
                    {
                        "path": str(clip_path),
                        "start_seconds": round(w_start, 2),
                        "end_seconds": round(w_end, 2),
                        "duration_seconds": round(w_end - w_start, 2),
                    }
                )

        if not clips:
            return ToolResult(
                success=False,
                error="Failed to cut any clips.",
                data={"metadata": meta},
            )

        # 5. Write manifest
        manifest_path = output_dir / "manifest.json"
        self._update_manifest(
            manifest_path,
            {
                "id": video_id,
                "url": url,
                "title": meta.get("title", ""),
                "uploader": meta.get("uploader", ""),
                "language": language,
                "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "clips": clips,
            },
        )

        elapsed = round(time.time() - start, 2)
        return ToolResult(
            success=True,
            data={
                "clips": [c["path"] for c in clips],
                "manifest_path": str(manifest_path),
                "source_title": meta.get("title", ""),
                "source_uploader": meta.get("uploader", ""),
                "clip_count": len(clips),
                "speech_segments_detected": len(speech_segments),
            },
            artifacts=[c["path"] for c in clips],
            duration_seconds=elapsed,
        )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _download_audio(self, url: str, output_dir: Path) -> tuple[Path | None, dict]:
        """Download best audio via yt-dlp CLI and convert to 16k mono WAV."""
        tmp_dir = output_dir / ".tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        audio_tmpl = str(tmp_dir / "source.%(ext)s")

        # Metadata first
        meta = self._extract_metadata(url)

        ydl_cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "-x", "--audio-format", "wav",
            "--audio-quality", "0",
            "-o", audio_tmpl,
            "--no-playlist",
            "--no-warnings",
            "--quiet",
            # Fallback player clients avoid YouTube 403 Forbidden on audio-only.
            "--extractor-args", "youtube:player_client=android,web_embedded,web_safari",
            url,
        ]
        try:
            self.run_command(ydl_cmd, timeout=300)
        except Exception as exc:
            return None, {"error": str(exc), **meta}

        # Find downloaded wav
        wav = self._find_file(tmp_dir, "source", [".wav", ".m4a", ".mp3", ".opus", ".webm"])
        if wav is None:
            return None, {"error": "downloaded audio not found", **meta}

        # Normalize to 16k mono WAV for reliable silence detection
        norm = tmp_dir / "source_16k.wav"
        try:
            self.run_command(
                [
                    "ffmpeg", "-y", "-i", str(wav),
                    "-vn", "-ac", "1", "-ar", "16000",
                    "-acodec", "pcm_s16le", str(norm),
                ],
                timeout=120,
            )
            return norm, meta
        except Exception:
            return wav, meta

    def _extract_metadata(self, url: str) -> dict:
        try:
            res = subprocess.run(
                [
                    "yt-dlp", "--dump-json", "--no-playlist",
                    "--no-warnings", "--skip-download", url,
                ],
                capture_output=True, text=True, timeout=60,
            )
            if res.returncode == 0 and res.stdout.strip():
                info = json.loads(res.stdout.strip().splitlines()[0])
                return {
                    "id": info.get("id", ""),
                    "title": info.get("title", ""),
                    "uploader": info.get("uploader", info.get("channel", "")),
                    "duration": info.get("duration", 0),
                }
        except Exception:
            pass
        return {"id": "", "title": "", "uploader": "", "duration": 0}

    def _detect_speech(
        self, audio_path: Path, silence_db: float, min_gap: float
    ) -> list[dict]:
        """Detect speech segments as the inverse of silence via silencedetect."""
        cmd = [
            "ffmpeg", "-i", str(audio_path),
            "-af", f"silencedetect=noise={silence_db}dB:d=0.3",
            "-f", "null", "-",
        ]
        try:
            res = self.run_command(cmd, timeout=300)
            output = res.stderr
        except Exception as exc:
            output = str(exc)

        starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", output)]
        ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", output)]

        total = self._get_duration(audio_path)
        silences = [
            {"start": s, "end": e}
            for s, e in zip(starts, ends)
        ]

        # Invert to speech segments
        speech = []
        cursor = 0.0
        for sil in silences:
            if sil["start"] > cursor:
                speech.append({"start": cursor, "end": sil["start"]})
            cursor = max(cursor, sil["end"])
        if cursor < total:
            speech.append({"start": cursor, "end": total})

        # Drop tiny fragments and merge close gaps
        merged = []
        for seg in speech:
            dur = seg["end"] - seg["start"]
            if dur < 0.5:
                continue
            if merged and (seg["start"] - merged[-1]["end"]) < min_gap:
                merged[-1]["end"] = seg["end"]
            else:
                merged.append(seg)
        return merged

    def _build_windows(
        self, speech_segments: list[dict], target: float, max_segments: int
    ) -> list[tuple[float, float]]:
        """Pack speech segments into ~target-length windows.

        Long continuous speech (no silence) is split into consecutive
        target-length chunks so every clip lands in the 15-20s range.
        """
        windows: list[tuple[float, float]] = []

        # First, merge close speech segments into continuous runs.
        runs: list[tuple[float, float]] = []
        for seg in speech_segments:
            if runs and (seg["start"] - runs[-1][1]) < 0.6:
                runs[-1] = (runs[-1][0], seg["end"])
            else:
                runs.append((seg["start"], seg["end"]))

        # Then slice each run into target-length windows.
        for run_start, run_end in runs:
            cursor = run_start
            while cursor < run_end:
                window_end = min(cursor + target, run_end)
                # Only keep windows that are at least 5s (avoid tiny tails).
                if window_end - cursor >= 5.0:
                    windows.append((cursor, window_end))
                cursor = window_end

        # Trim to max_segments, preferring longest windows.
        windows.sort(key=lambda w: w[1] - w[0], reverse=True)
        return windows[:max_segments]

    def _cut_clip(
        self, audio_path: Path, clip_path: Path, start: float, end: float
    ) -> bool:
        try:
            self.run_command(
                [
                    "ffmpeg", "-y",
                    "-i", str(audio_path),
                    "-ss", f"{start:.3f}",
                    "-to", f"{end:.3f}",
                    "-vn",
                    "-acodec", "libmp3lame",
                    "-ar", "44100",
                    "-b:a", "192k",
                    str(clip_path),
                ],
                timeout=60,
            )
            return clip_path.exists() and clip_path.stat().st_size > 1000
        except Exception:
            return False

    def _get_duration(self, path: Path) -> float:
        try:
            res = self.run_command(
                [
                    "ffprobe", "-v", "quiet",
                    "-show_entries", "format=duration",
                    "-of", "json", str(path),
                ]
            )
            return float(json.loads(res.stdout)["format"]["duration"])
        except Exception:
            return 0.0

    def _find_file(self, directory: Path, prefix: str, extensions: list[str]) -> Path | None:
        for ext in extensions:
            candidates = list(directory.glob(f"{prefix}*{ext}"))
            if candidates:
                return candidates[0]
        return None

    def _update_manifest(self, manifest_path: Path, entry: dict) -> None:
        manifest = {"version": "1.0", "samples": []}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = {"version": "1.0", "samples": []}
        manifest.setdefault("samples", []).append(entry)
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
