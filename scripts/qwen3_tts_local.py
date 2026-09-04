#!/usr/bin/env python3
"""Qwen3-TTS Local voice cloning / custom voice — CLI helper.

Lists reference audio in resource/asset folders, clones a voice from a chosen
clip, or synthesizes with the premium 'Sohee' (Korean) speaker.

Examples:
  # List reference audio candidates
  python scripts/qwen3_tts_local.py discover

  # Clone a voice from voice_library/comfort_heal.wav (bare name is auto-matched)
  python scripts/qwen3_tts_local.py clone --ref comfort_heal.wav --text "안녕하세요" --out out.wav

  # Premium Korean speaker with style instruction
  python scripts/qwen3_tts_local.py custom --speaker Sohee --text "안녕하세요" --instruct "잔잔하고 따뜻하게" --out out.wav
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.audio.qwen3_tts_local import Qwen3TTSLocal  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Qwen3-TTS local (voice clone / custom voice)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="list reference audio candidates")
    d.add_argument("--root", default=None, help="optional custom scan root")

    c = sub.add_parser("clone", help="zero-shot voice clone from a reference clip")
    c.add_argument("--ref", required=True, help="reference audio (path or bare filename)")
    c.add_argument("--ref-text", default="", help="transcript of the reference clip")
    c.add_argument("--text", required=True, help="text to synthesize")
    c.add_argument("--lang", default="Korean")
    c.add_argument("--out", default="qwen3_tts_clone.wav")

    v = sub.add_parser("custom", help="premium speaker (default Korean 'Sohee')")
    v.add_argument("--speaker", default="Sohee")
    v.add_argument("--text", required=True, help="text to synthesize")
    v.add_argument("--lang", default="Korean")
    v.add_argument("--instruct", default="", help="optional style instruction")
    v.add_argument("--out", default="qwen3_tts_custom.wav")

    a = p.parse_args()
    tool = Qwen3TTSLocal()

    if a.cmd == "discover":
        r = tool.execute({"mode": "discover_references", "reference_audio": a.root})
        if not r.success:
            print(r.error, file=sys.stderr)
            return 1
        for x in r.data["references"]:
            dur = f"{x['duration_seconds']}s" if x["duration_seconds"] else "?"
            print(f"{x['name']:40s} {dur:>8s}  {x['path']}")
        print(f"\n{len(r.data['references'])} clips found")
        return 0

    payload = {
        "mode": "clone" if a.cmd == "clone" else "custom_voice",
        "text": a.text,
        "language": a.lang,
        "output_path": a.out,
    }
    if a.cmd == "clone":
        payload["reference_audio"] = a.ref
        payload["reference_text"] = a.ref_text
    else:
        payload["speaker"] = a.speaker
        if a.instruct:
            payload["instruct"] = a.instruct

    r = tool.execute(payload)
    if not r.success:
        print(f"FAIL: {r.error}", file=sys.stderr)
        return 1
    print(f"OK  -> {r.data['output']}  ({r.data.get('duration_seconds')}s, {r.data.get('generation_seconds')}s gen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
