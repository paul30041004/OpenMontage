"""Assemble edit_decisions for the Genesis 8 short (Remotion, templated mode)."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.checkpoint import write_checkpoint

P = Path("projects")
pid = "genesis-8-after-the-rain"
proj = P / pid

narr = json.loads((proj / "artifacts/narration_durations.json").read_text())
script = json.loads((proj / "artifacts/script.json").read_text())

LEAD_IN = 0.4
GAP = 0.22
tempo = narr["atempo_scale"]

# --- narration timeline ---
segs = narr["segments_t60"]
starts = {}
t = LEAD_IN
for s in segs:
    starts[s["id"]] = t
    t += s["duration"] + GAP
narr_end = t - GAP
TOTAL = narr_end + 1.0
print(f"narration {LEAD_IN:.2f}..{narr_end:.2f}s, total {TOTAL:.2f}s")

# mix narration into one file: each segment delayed to its exact timeline start
full = proj / "assets/audio/narration_full_t60.wav"
in_args = []
fc_parts = []
mix_labels = []
for i, s in enumerate(segs):
    src = str(Path(s["path"]).resolve())
    in_args += ["-i", src]
    delay_ms = int(round(starts[s["id"]] * 1000))
    fc_parts.append(
        f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,"
        f"adelay={delay_ms}|{delay_ms}[a{i}]")
    mix_labels.append(f"[a{i}]")
fc_parts.append(
    "".join(mix_labels) + f"amix=inputs={len(segs)}:normalize=0,"
    f"apad=whole_dur={TOTAL:.3f}[out]")
subprocess.run(
    ["ffmpeg", "-y", "-v", "error"] + in_args +
    ["-filter_complex", ";".join(fc_parts), "-map", "[out]",
     "-ar", "44100", "-ac", "2", str(full)],
    check=True)
fdur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "csv=p=0", str(full)]).decode().strip())
print("mixed narration:", round(fdur, 2), "s")

# --- scene → narration window mapping (scene_plan order) ---
sc_by_section = {}
plan = json.loads((proj / "artifacts/scene_plan.json").read_text())
for sc in plan["scenes"]:
    sc_by_section.setdefault(sc["script_section_id"], []).append(sc)

# weights for splitting a section's window across its scenes (from plan proportions)
def split_windows_helper(section_id, w0, w1):
    scs = sc_by_section.get(section_id, [])
    if len(scs) == 1:
        return [(scs[0], w0, w1)]
    if section_id == "s01":      # video hook deserves the longer share
        weights = [0.62, 0.38]
    elif section_id == "s05":    # 3 hero beats, slightly weighted to first
        weights = [0.36, 0.34, 0.30]
    elif section_id == "s08":    # promise then harvest
        weights = [0.5, 0.5]
    else:
        weights = [1 / len(scs)] * len(scs)
    spans, cur = [], w0
    total_w = sum(weights)
    for i, sc in enumerate(scs):
        w = weights[i] / total_w
        end = w1 if i == len(scs) - 1 else cur + (w1 - w0) * w
        spans.append((sc, cur, end))
        cur = end
    return spans

cuts = []
cursor = LEAD_IN
for s in segs:
    w0, w1 = starts[s["id"]], starts[s["id"]] + s["duration"]
    for sc, c0, c1 in split_windows_helper(s["id"], w0, w1):
        if sc["id"] == "sc21":
            cuts.append({
                "id": "cut_sc21", "source": "sc21_textcard",
                "in_seconds": round(c0, 2), "out_seconds": round(TOTAL, 2),
                "layer": "primary", "type": "text_card",
                "text": "창세기 8장 22절",
                "subtitle": "땅이 있는 한 파종과 거둠은 그치지 않습니다",
                "transition_in": "slow-crossfade", "transition_duration": 0.8,
                "backgroundColor": "#0A141C",
                "reason": "약속의 원문으로 마무리하는 엔딩 카드",
            })
            continue
        src = f"vis_{sc['id']}"
        anim = "ken-burns-slow-zoom"
        if sc["id"] == "sc12":
            anim = "ken-burns-slow-drift-up"
        if sc["id"] in ("sc01", "sc09"):
            anim = None
        cut = {
            "id": f"cut_{sc['id']}", "source": src,
            "in_seconds": round(c0, 2), "out_seconds": round(c1, 2),
            "layer": "primary",
            "transform": {"animation": anim} if anim else {},
            "transition_in": "slow-crossfade" if sc["id"] != "sc01" else "fade",
            "transition_duration": 0.6,
            "backgroundColor": "#0A141C",
            "reason": sc["shot_intent"],
        }
        if sc["id"] in ("sc01", "sc09"):
            del cut["transform"]
        cuts.append(cut)

def split_windows_helper(section_id, w0, w1):
    """compat shim kept separate from the walrus above"""
    scs = sc_by_section.get(section_id, [])
    if len(scs) == 1:
        return [(scs[0], w0, w1)]
    if section_id == "s01":
        weights = [0.62, 0.38]
    elif section_id == "s05":
        weights = [0.36, 0.34, 0.30]
    elif section_id == "s08":
        weights = [0.5, 0.5]
    else:
        weights = [1 / len(scs)] * len(scs)
    spans, cur = [], w0
    tw = sum(weights)
    for i, sc in enumerate(scs):
        w = weights[i] / tw
        end = w1 if i == len(scs) - 1 else cur + (w1 - w0) * w
        spans.append((sc, cur, end))
        cur = end
    return spans

# --- word-level karaoke captions from section texts (proportional weighting) ---
captions = []
for s in segs:
    sec = next(x for x in script["sections"] if x["id"] == s["id"])
    words = sec["text"].split()
    w0 = starts[s["id"]]
    dur = s["duration"]
    weights = [max(len(w), 1) for w in words]
    tw = sum(weights)
    cur_ms = w0 * 1000
    for i, w in enumerate(words):
        d_ms = dur * 1000 * weights[i] / tw
        captions.append({
            "word": w,
            "startMs": round(cur_ms),
            "endMs": round(cur_ms + d_ms),
            "pageBreakAfter": False,
        })
        cur_ms += d_ms
    if captions:
        captions[-1]["pageBreakAfter"] = True

# --- slideshow risk ---
from lib.slideshow_risk import score_slideshow_risk
scenes = plan["scenes"]
risk = score_slideshow_risk(scenes, renderer_family="remotion")
print("slideshow risk:", risk.get("verdict"), risk.get("average"))

edit = {
    "version": "1.0",
    "cuts": cuts,
    "overlays": [],
    "audio": {
        "narration": {
            "src": "assets/audio/narration_full_t60.wav",
            "volume": 1.0,
            "segments": [
                {"asset_id": f"narr_{s['id']}_t60",
                 "start_seconds": round(starts[s["id"]], 2),
                 "end_seconds": round(starts[s["id"]] + s["duration"], 2)}
                for s in segs
            ],
        },
        "music": {
            "asset_id": "bgm_final",
            "src": "assets/music/bgm_final.wav",
            "volume": 0.18,
            "fade_in_seconds": 2.0,
            "fade_out_seconds": 2.0,
            "loop": False,
            "ducking": {
                "enabled": True,
                "threshold_db": -6,
                "reduction_db": -10,
                "attack_ms": 200,
                "release_ms": 600,
            },
        },
        "sfx": [],
    },
    "subtitles": {
        "enabled": True,
        "style": "karaoke",
        "font": "Noto Sans KR",
        "font_size": 56,
        "color": "#F5EFE2",
        "outline_color": "#0A141C",
        "background": "#0A141C99",
        "position": "bottom-center",
        "max_words_per_line": 5,
    },
    "captions": captions,
    "transitions": [],
    "renderer_family": "documentary-montage",
    "render_runtime": "remotion",
    "composition_mode": "templated",
    "slideshow_risk_score": {"average": risk.get("average"), "verdict": risk.get("verdict")},
    "metadata": {
        "total_duration_seconds": TOTAL,
        "narration_end_seconds": round(narr_end, 2),
        "tempo_scale": tempo,
        "source_plan": "scene_plan.json + narration_durations.json (measured)",
    },
}

from jsonschema import validate
schema = json.loads((Path(".") / "schemas/artifacts/edit_decisions.schema.json").read_text())
validate(edit, schema)

(proj / "artifacts/edit_decisions.json").write_text(json.dumps(edit, ensure_ascii=False, indent=2))
print(f"edit_decisions written: {len(cuts)} cuts, {len(captions)} karaoke captions, total {TOTAL:.2f}s")
