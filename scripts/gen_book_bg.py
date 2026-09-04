#!/usr/bin/env python3
"""Generate the book-style backdrop at any resolution (16:9 / 9:16 / 4:3).

Safe zones are ratio-aware:
  - top band  ~10% height: title
  - bottom band ~22% height: karaoke subtitle + pop layer (no overlap)
  - decorative motifs stay in the center band
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RATIOS = {"16:9": (1280, 720), "9:16": (720, 1280), "4:3": (1280, 960)}


def build_html(w: int, h: int) -> str:
    top = int(h * 0.10)
    bottom = h - int(h * 0.22)
    return f"""<html><head><meta charset="utf-8"><style>
@page {{ size: {w}px {h}px; margin: 0 }}
html,body {{ margin:0; padding:0; width:{w}px; height:{h}px; background:#f5efdf; }}
.page {{ position:relative; width:{w}px; height:{h}px; }}
.series {{ position:absolute; top:{top//3}px; right:{w//14}px; font-family:'Nanum Myeongjo',serif; font-size:{max(16, w//56)}px; letter-spacing:5px; color:#8a7f6a; }}
.thread {{ position:absolute; top:{top//3}px; left:{w//14}px; height:3px; width:{max(60, w//12)}px; background:#b3352e; }}
.thread::after {{ content:''; position:absolute; right:-7px; top:-8px; width:19px; height:19px; border-radius:50%; background:#b3352e; }}
.verse-bg {{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font-family:'Nanum Myeongjo',serif; font-size:{max(90, h//3)}px; color:rgba(43,38,32,0.05); }}
.corner {{ position:absolute; bottom:{h - bottom + 30}px; right:{w//14}px; font-family:'Nanum Myeongjo',serif; font-size:{max(14, w//72)}px; color:#b8ad94; }}
</style></head><body>
<div class="page">
  <div class="series">붉 은 실  시 리 즈</div>
  <div class="thread"></div>
  <div class="verse-bg">말씀</div>
  <div class="corner">MALSSEUM</div>
</div></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "projects" / "series-batch" / "shared"))
    ap.add_argument("--ratios", nargs="*", default=["16:9", "9:16", "4:3"])
    args = ap.parse_args()

    from tools.graphics.ebook_gen import EbookGen

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    eg = EbookGen()
    for ratio in args.ratios:
        w, h = RATIOS[ratio]
        png = outdir / f"book_bg_{ratio.replace(':', 'x')}.png"
        mp4 = outdir / f"book_bg_{ratio.replace(':', 'x')}.mp4"
        r = eg.execute({"renderer": "weasyprint", "use": "html",
                        "html": build_html(w, h), "format": "frame",
                        "width": w, "height": h, "output_path": str(png)})
        if not r.success:
            print("bg failed:", ratio, r.error)
            continue
        # subtle Ken Burns video
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(png), "-t", "12.5", "-r", "24",
            "-vf", f"scale={int(w*1.05)}:{int(h*1.05)},"
                   f"zoompan=z='min(zoom+0.0008,1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:fps=24:s={w}x{h}",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(mp4)],
            check=True, capture_output=True)
        print(f"{ratio}: {w}x{h} -> {mp4}")


if __name__ == "__main__":
    main()
