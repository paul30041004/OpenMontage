#!/usr/bin/env python3
"""Batch Bible-episode generator — full local stack on MacBook CPU.

For each episode: supertonic TTS narration -> wav2lip avatar (real PD portrait)
-> composite over a shared CG cinematic backdrop with title + Korean subtitles
+ BGM bed. Outputs projects/series-batch/E<NN>/episode.mp4.

Usage:
  python scripts/batch_bible_episodes.py [--bg <graded.mp4>] [--outdir projects/series-batch]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EPISODES = [
    {
        "id": "E01", "book": "시편 121편", "title": "나의 도움이 어디서 올까",
        "emotion": "잔잔하고 따뜻하며 위로하는 감정",
        "narration": "내가 산을 향하여 눈을 들리라. 나의 도움이 어디서 올까. 나의 도움은 천지를 지으신 여호와에게서로다.",
        "srt": [
            ("00:00:00,900", "00:00:05,500", "내가 산을 향하여 눈을 들리라"),
            ("00:00:05,800", "00:00:11,500", "나의 도움이 어디서 올까"),
        ],
    },
    {
        "id": "E02", "book": "요한복음 3:16", "title": "하나님이 세상을 사랑하사",
        "emotion": "절절하고 감동적인 사랑의 감정",
        "narration": "하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니, 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라.",
        "srt": [
            ("00:00:00,900", "00:00:06,000", "하나님이 세상을 이처럼 사랑하사"),
            ("00:00:06,300", "00:00:12,500", "독생자를 주셨으니"),
        ],
    },
    {
        "id": "E03", "book": "마태복음 11:28", "title": "수고하고 무거운 짐 진 자들아",
        "emotion": "부드럽고 다정하게 위로하는 목소리",
        "narration": "수고하고 무거운 짐 진 자들아, 다 내게로 오라. 내가 너희를 쉬게 하리라.",
        "srt": [
            ("00:00:00,900", "00:00:06,000", "수고하고 무거운 짐 진 자들아"),
            ("00:00:06,300", "00:00:11,500", "다 내게로 오라. 내가 쉬게 하리라"),
        ],
    },
]

PORTRAIT = ROOT / "projects" / "avatar-bible-psalm23" / "portrait.jpg"
BGM = ROOT / "projects" / "book-proverbs-3" / "assets" / "music" / "bgm.mp3"
FONT = "NanumGothic"


def sh(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {(p.stderr or p.stdout)[-500:]}")


def dt(text: str) -> str:
    """Escape a value for use inside a drawtext option (':' and quotes)."""
    return text.replace(":", r"\:").replace("'", r"\'")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True, help="book-style backdrop mp4 (ebook_gen based)")
    ap.add_argument("--outdir", default=str(ROOT / "projects" / "series-batch"))
    ap.add_argument("--avatar-height", type=int, default=600)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    bg = Path(args.bg)

    for ep in EPISODES:
        edir = outdir / ep["id"]
        (edir / "audio").mkdir(parents=True, exist_ok=True)
        (edir / "work").mkdir(parents=True, exist_ok=True)

        print(f"\n=== {ep['id']}: {ep['book']} — {ep['title']} ===")

        # 1) TTS (VoxCPM2 emotional acting via the OpenMontage tool)
        narration = edir / "audio" / "narration.wav"
        p = subprocess.run([sys.executable, "-c", f"""
from tools.audio.voxcpm_tts import VoxCPMTTS
r = VoxCPMTTS().execute({{
    'text': r'{ep["narration"]}',
    'emotion': r'{ep.get("emotion", "")}',
    'output_path': r'{narration}',
    'device': 'mps',
}})
assert r.success, r.error
"""], capture_output=True, text=True, cwd=str(ROOT))
        if p.returncode != 0:
            raise RuntimeError(f"TTS failed: {(p.stderr or p.stdout)[-400:]}")

        # 2) avatar (rhubarb lip-sync, composited over the book backdrop)
        avatar = edir / "work" / "avatar.mp4"
        p = subprocess.run([sys.executable, "-c", f"""
from tools.avatar.rhubarb_lipsync import RhubarbLipsync
r = RhubarbLipsync().execute({{
    'audio_path': r'{narration}',
    'output_path': r'{avatar}',
    'bg_path': r'{bg}',
    'fps': 24,
}})
assert r.success, r.error
"""], capture_output=True, text=True, cwd=str(ROOT))
        if p.returncode != 0:
            raise RuntimeError(f"avatar failed: {p.stderr[-500:]}")

        # 3) subtitles
        srt = edir / "work" / "subs.srt"
        lines = []
        for i, (t0, t1, text) in enumerate(ep["srt"], 1):
            lines += [str(i), f"{t0} --> {t1}", text, ""]
        srt.write_text("\n".join(lines), encoding="utf-8")

        # 4) composite: title + subtitles + BGM over the rhubarb composite
        final = edir / "episode.mp4"
        book_t = dt(ep["book"])
        title_t = dt(ep["title"])
        sh(["ffmpeg", "-y", "-i", str(avatar), "-i", str(BGM),
            "-filter_complex",
            f"[0:v]drawtext=font={FONT}:text='{book_t}':fontsize=56:fontcolor=0x2B2620:borderw=2:bordercolor=white@0.8:x=40:y=32,"
            f"drawtext=font={FONT}:text='{title_t}':fontsize=42:fontcolor=0xB3352E:borderw=2:bordercolor=white@0.8:x=40:y=98,"
            f"subtitles={srt}:force_style='FontName={FONT},FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=42'[v];"
            f"[1:a]atrim=0:12.5,afade=t=in:st=0:d=1.5,afade=t=out:st=10.5:d=2,volume=0.22[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", str(final)])
        print(f"  -> {final}")


if __name__ == "__main__":
    main()
