#!/usr/bin/env python3
"""interpolate_frames.py — Create smooth motion interpolation between sequential keyframe images.

Stretches storyboard keyframes into longer video transitions using FFmpeg's
`minterpolate` motion compensation filter (MCI / optical flow or blend mode).

Usage:
  python3 interpolate_frames.py --input-dir ./frames --output ./interpolated.mp4 \
      --duration-per-frame 2.0 --target-fps 30 --mode mci
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def create_slideshow_with_interpolation(
    frame_paths: list[Path],
    output_mp4: Path,
    duration_per_frame: float = 2.0,
    target_fps: int = 30,
    mode: str = "mci",  # mci (motion compensation) or blend
) -> Path:
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_mp4.parent / "_temp_interp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    concat_txt = temp_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for p in frame_paths:
            f.write(f"file '{p.resolve()}'\n")
            f.write(f"duration {duration_per_frame}\n")
        # repeat last frame once for ffmpeg concat demuxer contract
        f.write(f"file '{frame_paths[-1].resolve()}'\n")

    raw_mp4 = temp_dir / "raw_stepped.mp4"
    # 1. Create stepped video from images
    cmd_step = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-vf", f"fps={target_fps},scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast",
        str(raw_mp4)
    ]
    subprocess.run(cmd_step, check=True)

    # 2. Apply minterpolate for smooth optical flow transitions between frames
    interp_filter = (
        f"minterpolate='fps={target_fps}:mi_mode={mode}:mc_mode=aobmc:vsbmc=1'"
        if mode == "mci"
        else f"minterpolate='fps={target_fps}:mi_mode=blend'"
    )

    cmd_interp = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_mp4),
        "-vf", interp_filter,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        str(output_mp4)
    ]
    subprocess.run(cmd_interp, check=True)

    # clean up temp stepped file
    if raw_mp4.exists():
        raw_mp4.unlink()
    if concat_txt.exists():
        concat_txt.unlink()
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    return output_mp4


def main() -> None:
    ap = argparse.ArgumentParser(description="Interpolate between sequential storyboard frames")
    ap.add_argument("--input-dir", "-i", required=True, help="Directory containing sliced frame images")
    ap.add_argument("--output", "-o", required=True, help="Output MP4 file path")
    ap.add_argument("--duration-per-frame", "-d", type=float, default=2.0,
                    help="Seconds to hold/transition each keyframe (default: 2.0s)")
    ap.add_argument("--target-fps", type=int, default=30, help="Output framerate (default: 30)")
    ap.add_argument("--mode", choices=["mci", "blend"], default="blend",
                    help="Interpolation mode: mci (optical flow motion compensation) or blend (fast cross-dissolve)")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    frames = sorted([p for p in in_dir.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
    if len(frames) < 2:
        sys.exit(f"At least 2 frames required in {in_dir}")

    out = create_slideshow_with_interpolation(
        frames, Path(args.output), args.duration_per_frame, args.target_fps, args.mode
    )
    print(f"Interpolation complete: {out}")


if __name__ == "__main__":
    main()
