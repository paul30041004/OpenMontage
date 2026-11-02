"""Batch narration generation — Qwen3-TTS local Sohee (CustomVoice).

Unification contract (d-012): speaker/language/instruct byte-identical across
all segments; only `text` varies. Anchor = s06 sample (already approved path).
Writes partial_progress checkpoints after each segment.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.checkpoint import write_checkpoint
from tools.tool_registry import registry

P = Path("projects")
pid = "genesis-8-after-the-rain"
ROOT = Path(".")
script = json.loads((P / pid / "artifacts/script.json").read_text())

INSTRUCT = "따뜻하고 낮은 감성 내레이션, 성경 구절을 위로하듯 낭독, 자연스러운 다큐멘터리 속도"

registry.discover()
tts = registry._tools["qwen3_tts_local"]

out_dir = P / pid / "assets/audio"
out_dir.mkdir(parents=True, exist_ok=True)

segments = []
for i, sec in enumerate(script["sections"], 1):
    out = out_dir / f"narr_{sec['id']}.wav"
    if out.exists():
        dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(out)]).decode().strip())
        segments.append({"id": sec["id"], "path": str(out), "duration": dur})
        print(f"[skip] {sec['id']} {dur:.2f}s")
        continue
    r = tts.execute({
        "mode": "custom_voice",
        "text": sec["text"],
        "speaker": "Sohee",
        "language": "Korean",
        "instruct": INSTRUCT,
        "output_path": str(out),
    })
    if not r.success:
        raise SystemExit(f"FAILED {sec['id']}: {r.error}")
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(out)]).decode().strip())
    segments.append({"id": sec["id"], "path": str(out), "duration": dur})
    print(f"[ok] {sec['id']} {dur:.2f}s")

    write_checkpoint(
        P, pid, "assets", "in_progress", {},
        pipeline_type="short-form-factory",
        metadata={"partial_progress": {
            "completed_narration": segments,
            "narration_provider": "qwen3_local Sohee",
        }},
    )

total = sum(s["duration"] for s in segments)
print(f"TOTAL narration: {total:.2f}s across {len(segments)} segments")
(P / pid / "artifacts/narration_durations.json").write_text(
    json.dumps({"provider": "qwen3_local Sohee", "instruct": INSTRUCT,
                "anchor": str(out_dir / "qwen3_s06_test.wav"), "segments": segments,
                "total": total}, ensure_ascii=False, indent=2))
