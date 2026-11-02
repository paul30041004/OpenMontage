"""Pre-compose asset prep + CinematicRenderer props for the Genesis 8 short.

1. Ken-Burns video clips from the 18 portrait stills (exact scene durations)
2. Trim pexels video clips to scene durations
3. Ducking pre-mix (narration + sidechain-ducked BGM) into one soundtrack
4. Stage everything into remotion-composer/public/assets/...
5. Emit composition props (scenes + soundtrack + captions) for remotion_render
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

P = Path("projects")
pid = "genesis-8-after-the-rain"
proj = P / pid
PUBLIC = Path("remotion-composer/public/assets")

edit = json.loads((proj / "artifacts/edit_decisions.json").read_text())
cuts = edit["cuts"]

# ---------- 1. ken-burns + trim clips ----------
tmp = proj / "assets/clips"
tmp.mkdir(parents=True, exist_ok=True)
PUBLIC.mkdir(parents=True, exist_ok=True)

vis = {a["id"]: a for a in json.loads((proj / "artifacts/asset_manifest.json").read_text())["assets"]}

def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg failed: {' '.join(args[:6])}\n{r.stderr[-800:]}")

for i, cut in enumerate(cuts):
    sid = cut["source"]
    a = vis.get(sid)
    dur = cut["out_seconds"] - cut["in_seconds"]
    out_rel = f"assets/video/{sid}_slice.mp4"
    dst = Path("remotion-composer/public") / out_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        continue
    if a is None:
        continue
    src = proj / a["path"]
    if not src.is_file():
        continue
    if a["type"] == "video":
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(cut["in_seconds"]),
             "-t", str(dur), "-i", str(src),
             "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
             "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(dst)])
    else:
        zoom_dir = "zoompan=z='min(1.001+0.0006*on,1.10)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2'" \
            if i % 2 == 0 else \
            "zoompan=z='min(1.08-0.0006*on,1.001)':x='iw/2-(iw/zoom)/2':y='ih/3-(ih/zoom)/3'"
        frames = int(round(dur * 30)) + 1
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(src),
             "-vf",
             f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
             f"{zoom_dir}:d={frames}:s=1080x1920:fps=30",
             "-t", str(dur), "-an", "-c:v", "libx264", "-crf", "18",
             "-pix_fmt", "yuv420p", str(dst)])
    print(f"[clip] {sid} {dur:.2f}s")

# ---------- 2. audio duck-mix ----------
audio = proj / "assets/audio"
mixed = proj / "assets/audio/mixed_final.wav"
if not mixed.exists():
    fc = (
        "[1:a]asplit=2[n1][n2];"
        "[0:a]volume=0.7[bg0];"
        "[bg0][n1]sidechaincompress=threshold=0.03:ratio=12:attack=120:release=500[bg];"
        "[n2][bg]amix=inputs=2:duration=longest:normalize=0,"
        "afade=t=out:st=61.5:d=1.9[out]"
    )
    run(["ffmpeg", "-y", "-v", "error",
         "-i", str(proj / "assets/music/bgm_final.wav"),
         "-i", str(audio / "narration_full_t60.wav"),
         "-filter_complex", fc, "-map", "[out]",
         "-ar", "44100", "-ac", "2", str(mixed)])
print("duck-mix skipped-if-exists")

# ---------- 3. stage single soundtrack ----------
(mixed.is_file()) or run(["ffmpeg", "-y", "-v", "error", "-i", str(audio / "narration_full_t60.wav"), str(mixed)])
scenes = []
for i, cut in enumerate(cuts):
    if cut.get("type") == "text_card":
        scenes.append({
            "id": cut["id"], "kind": "title",
            "startSeconds": cut["in_seconds"],
            "durationSeconds": cut["out_seconds"] - cut["in_seconds"],
            "text": cut["text"],
            "accent": "#C9A227", "variant": "reveal",
        })
        continue
    dur = round(cut["out_seconds"] - cut["in_seconds"], 3)
    scenes.append({
        "id": cut["id"], "kind": "video",
        "startSeconds": cut["in_seconds"],
        "durationSeconds": dur,
        "src": f"assets/video/{cut['source']}_slice.mp4",
        "tone": "steel",
        "fadeInFrames": 8, "fadeOutFrames": 8,
    })

captions = {
    "words": edit["captions"],
    "wordsPerPage": 5,
    "fontSize": 58,
    "color": "#F5EFE2",
    "highlightColor": "#C9A227",
    "backgroundColor": "rgba(10,20,28,0.55)",
    "wordSeparator": "",
}

comp = {
    "scenes": scenes,
    "soundtrack": {
        "src": "assets/audio/mixed_final.wav",
        "volume": 1.0,
        "fadeInSeconds": 0.5,
        "fadeOutSeconds": 2.0,
        "trimBeforeSeconds": 0.0,
    },
    "captions": captions,
    "titleFontSize": 64,
    "titleWidth": 880,
    "signalLineCount": 10,
}

import shutil
shutil.copy2(mixed, Path("remotion-composer/public") / "assets/audio/mixed_final.wav")
Path("remotion-composer/public/assets/audio/mixed_final.wav").parent.mkdir(parents=True, exist_ok=True)

out = proj / "artifacts/composition_props.json"
out.write_text(json.dumps(comp, ensure_ascii=False, indent=2))
print(f"composition props written: {len(scenes)} scenes -> {out}")
