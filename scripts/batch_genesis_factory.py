#!/usr/bin/env python3
"""batch_genesis_factory.py — Production Engine for Genesis 100 Shorts Series.

Processes episodes from `genesis_100_manifest.json`:
1. Generates 3x3 Storyboard Grid via Google Flow (Nano Banana Pro)
2. Slices grid into 9 panels via slice_grid.py
3. Synthesizes emotional Korean eSports caster narration via VoxCPM2
4. Renders 9:16 vertical video via Remotion GenesisSeriesEpisode
5. Tracks and logs progress in genesis_100_manifest.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "projects" / "_genesis_100_series" / "genesis_100_manifest.json"
SHARED_BGM_PATH = REPO_ROOT / "projects" / "genesis4-cain-abel-esports" / "assets" / "music" / "bgm_esports_battle.mp3"
VOXCPM_ANCHOR = REPO_ROOT / "projects" / "genesis4-cain-abel-esports" / "assets" / "audio" / "voxcpm_anchor_sec01.wav"


def slice_grid_frames(img_path: Path, out_dir: Path, rows: int = 3, cols: int = 3) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(img_path)
    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows

    saved = []
    idx = 1
    for r in range(rows):
        for c in range(cols):
            left = c * cell_w
            top = r * cell_h
            right = left + cell_w
            bottom = top + cell_h
            cell = img.crop((left, top, right, bottom))
            target_path = out_dir / f"frame_{idx:02d}.png"
            cell.save(target_path)
            saved.append(target_path)
            idx += 1
    return saved


def generate_flow_grid(flow_image_tool: Any, prompt: str, out_path: Path) -> bool:
    print(f"  [Flow] Generating 3x3 storyboard grid...")
    res = flow_image_tool.execute({
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "output_path": str(out_path)
    })
    if not res.success:
        print(f"  [Flow Error] {res.error}")
        return False
    print(f"  [Flow] Success: {out_path.name}")
    return True


def synthesize_narration(voxcpm_tool: Any, sections: list[str], audio_dir: Path) -> Path:
    audio_dir.mkdir(parents=True, exist_ok=True)
    part_files = []

    for i, text in enumerate(sections, start=1):
        sec_out = audio_dir / f"sec_{i:02d}.wav"
        if not sec_out.exists():
            print(f"  [TTS] Synthesizing line {i}/{len(sections)}...")
            res = voxcpm_tool.execute({
                "text": text,
                "reference_audio": str(VOXCPM_ANCHOR),
                "emotion": "열정적인 e스포츠 캐스터 중계 톤으로, 빠르고 힘있게",
                "device": "mps",
                "timesteps": 8,
                "output_path": str(sec_out)
            })
            if not res.success:
                print(f"  [TTS Warning] Line {i} failed ({res.error}), copying anchor...")
                shutil.copy(VOXCPM_ANCHOR, sec_out)
        part_files.append(sec_out)

    # Concat all segments into master narration
    master_wav = audio_dir / "master_narration.wav"
    concat_txt = audio_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for pf in part_files:
            f.write(f"file '{pf.resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c:a", "pcm_s16le", str(master_wav)
    ], check=True)
    return master_wav


def render_remotion_episode(
    slug: str,
    title: str,
    chapter: int,
    part: int,
    subtitles: list[str],
    out_mp4: Path
) -> bool:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    props = {
        "projectDir": slug,
        "title": title,
        "chapter": chapter,
        "part": part,
        "subtitles": subtitles
    }
    props_json = out_mp4.parent / f".props_{slug}.json"
    props_json.write_text(json.dumps(props, ensure_ascii=False))

    composer_dir = REPO_ROOT / "remotion-composer"
    cmd = [
        "npx", "remotion", "render",
        "src/index.tsx",
        "GenesisSeriesEpisode",
        str(out_mp4.resolve()),
        f"--props={props_json.resolve()}"
    ]
    print(f"  [Remotion] Rendering 9:16 vertical short...")
    res = subprocess.run(cmd, cwd=str(composer_dir), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [Remotion Error] {res.stderr[-500:]}")
        return False
    print(f"  [Remotion] Finished: {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.1f} MB)")
    return True


def process_episode(ep: dict[str, Any], flow_tool: Any, voxcpm_tool: Any, force: bool = False) -> bool:
    ep_num = ep["episode_number"]
    slug = ep["slug"]
    title = ep["title"]
    chapter = ep["chapter"]
    part = ep["part"]

    proj_dir = REPO_ROOT / "projects" / slug
    renders_dir = proj_dir / "renders"
    final_mp4 = renders_dir / "final.mp4"

    if final_mp4.exists() and not force:
        print(f"[Ep {ep_num:03d}: {slug}] Already rendered, skipping.")
        return True

    print(f"\n=======================================================")
    print(f"▶ STARTING EPISODE {ep_num:03d} : {title} ({slug})")
    print(f"=======================================================")

    img_dir = proj_dir / "assets" / "images"
    audio_dir = proj_dir / "assets" / "audio"
    sliced_dir = img_dir / "sliced_frames"
    grid_img = img_dir / "storyboard_grid_3x3.png"

    # Step 1: Flow 3x3 Grid
    if not grid_img.exists() or force:
        ok = generate_flow_grid(flow_tool, ep["storyboard_prompt"], grid_img)
        if not ok:
            return False

    # Step 2: Slice Grid into 9 frames
    frames = slice_grid_frames(grid_img, sliced_dir)
    print(f"  [Slice] Sliced {len(frames)} frames into {sliced_dir.name}")

    # Step 3: Narration via VoxCPM2
    master_wav = synthesize_narration(voxcpm_tool, ep["script_sections"], audio_dir)

    # Step 4: Stage into Remotion public folder
    stage_dir = REPO_ROOT / "remotion-composer" / "public" / slug
    stage_dir.mkdir(parents=True, exist_ok=True)
    for f in frames:
        shutil.copy(f, stage_dir / f.name)
    shutil.copy(master_wav, stage_dir / "master_narration.wav")
    shutil.copy(SHARED_BGM_PATH, stage_dir / "bgm_esports.mp3")

    # Step 5: Render with Remotion
    ok = render_remotion_episode(slug, title, chapter, part, ep["script_sections"], final_mp4)
    if not ok:
        return False

    # Update manifest record
    ep["status"] = "completed"
    ep["project_dir"] = str(proj_dir.relative_to(REPO_ROOT))
    ep["render_path"] = str(final_mp4.relative_to(REPO_ROOT))
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch Genesis 100 Shorts Factory")
    parser.add_argument("--episode", type=int, help="Single episode number to render (1-100)")
    parser.add_argument("--start", type=int, default=1, help="Start episode number (default: 1)")
    parser.add_argument("--end", type=int, default=100, help="End episode number (default: 100)")
    parser.add_argument("--limit", type=int, help="Limit number of episodes to process")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing renders")
    args = parser.parse_args()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Discover tools
    from tools.tool_registry import registry
    registry.discover()
    flow_tool = registry._tools.get("flow_image")
    voxcpm_tool = registry._tools.get("voxcpm_tts")

    if not flow_tool or not voxcpm_tool:
        sys.exit("Error: flow_image or voxcpm_tts tool not available.")

    episodes = manifest["episodes"]
    if args.episode:
        targets = [ep for ep in episodes if ep["episode_number"] == args.episode]
    else:
        targets = [ep for ep in episodes if args.start <= ep["episode_number"] <= args.end]
        if args.limit:
            targets = targets[:args.limit]

    print(f"Batch Genesis Factory initialized. Target queue: {len(targets)} episodes.")

    success_count = 0
    for ep in targets:
        try:
            ok = process_episode(ep, flow_tool, voxcpm_tool, args.force)
            if ok:
                success_count += 1
                # Save updated manifest
                manifest["completed_count"] = sum(1 for e in episodes if e.get("status") == "completed")
                with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Error processing Episode {ep.get('episode_number')}]: {e}")

    print(f"\n=======================================================")
    print(f"BATCH PRODUCTION COMPLETE: {success_count}/{len(targets)} succeeded.")
    print(f"Total series progress: {manifest['completed_count']}/100 episodes completed.")
    print(f"=======================================================")


if __name__ == "__main__":
    main()
