"""상황별 anchor 음성 샘플 라이브러리 생성기.

각 상황(다큐/뉴스/감성/하이프/교육)에 맞는 anchor 샘플을 VoxCPM2로 생성하고
voice_library/에 저장한다. 이후 모든 롱폼/미드폼 내레이션은 이 샘플을
reference_audio로 클론하여 일관된 음성을 유지한다 (tts-sample-unification).

사용:
  python tools/audio/build_voice_library.py            # 전체 생성
  python tools/audio/build_voice_library.py --list    # 목록만
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
VOICE_LIB = ROOT / "voice_library"
VOICE_LIB.mkdir(parents=True, exist_ok=True)

# 상황별 보이스 정의 (voice_design은 영어, emotion은 한국어)
VOICE_PRESETS = {
    "documentary": {
        "label": "다큐멘터리 내레이션",
        "voice_design": "deep, authoritative, calm Korean male narrator, documentary style",
        "emotion": "깊고 묵직하게, 다큐멘터리 내레이션처럼 차분하게",
        "sample_text": "이것은 깊고 묵직한 다큐멘터리 내레이션의 기준 음성입니다.",
    },
    "news": {
        "label": "뉴스 앵커",
        "voice_design": "clear, confident, professional Korean male news anchor",
        "emotion": "명료하고 신뢰감 있게, 뉴스 앵커처럼 정확하게",
        "sample_text": "오늘의 주요 뉴스를 전해드리겠습니다.",
    },
    "emotional": {
        "label": "감성 위로",
        "voice_design": "warm, gentle, comforting Korean female narrator, soft and tender",
        "emotion": "따뜻하고 위로가 되게, 감성적으로 부드럽게",
        "sample_text": "당신의 마음에 따뜻한 위로가 되기를 바랍니다.",
    },
    "hype": {
        "label": "하이프/에너지",
        "voice_design": "energetic, powerful, charismatic Korean male narrator, hype style",
        "emotion": "강렬하고 에너지 넘치게, 하이프처럼 흥분해서",
        "sample_text": "지금 바로 시작합니다! 놓치지 마세요!",
    },
    "educational": {
        "label": "교육/설명",
        "voice_design": "friendly, clear, patient Korean male teacher, educational style",
        "emotion": "차분하고 친절하게, 설명하듯이 또박또박",
        "sample_text": "이 개념을 쉽게 설명해드리겠습니다.",
    },
}


def build_all(device: str = "mps", presets: dict = None, manifest_name: str = "voice_library.json") -> dict:
    from tools.tool_registry import registry
    registry.discover()
    voxcpm = registry._tools.get("voxcpm_tts")
    if not voxcpm or voxcpm.get_status().name != "AVAILABLE":
        print(json.dumps({"error": "VoxCPM2 not available"}, ensure_ascii=False))
        return {}

    presets = presets or VOICE_PRESETS
    manifest = {"version": "1.0", "voices": {}}
    for key, preset in presets.items():
        out_path = VOICE_LIB / f"{key}.wav"
        print(f"🎙️ [{key}] {preset['label']} 샘플 생성 중...")
        res = voxcpm.execute({
            "text": preset["sample_text"],
            "voice_design": preset["voice_design"],
            "emotion": preset["emotion"],
            "device": device,
            "output_path": str(out_path),
        })
        if res.success:
            manifest["voices"][key] = {
                "label": preset["label"],
                "voice_design": preset["voice_design"],
                "emotion": preset["emotion"],
                "sample_text": preset["sample_text"],
                "sample_path": str(out_path),
                "device": device,
            }
            print(f"   ✅ {out_path.name} ({res.data.get('duration_seconds', '?')}s)")
        else:
            print(f"   ❌ {res.error}")

    manifest_path = VOICE_LIB / manifest_name
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📦 {manifest_name} 저장 ({len(manifest['voices'])}개 보이스)")
    return manifest


def list_voices() -> dict:
    manifest_path = VOICE_LIB / "voice_library.json"
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    if "--list" in sys.argv:
        m = list_voices()
        print(json.dumps(m, ensure_ascii=False, indent=2))
    elif "--50" in sys.argv:
        # 50개 한국 숏폼 보이스 생성
        from tools.audio.voice_presets_50 import VOICE_PRESETS_50
        device = "cpu" if "--cpu" in sys.argv else "mps"
        build_all(device=device, presets=VOICE_PRESETS_50, manifest_name="voice_library_50.json")
    elif "--human" in sys.argv:
        # 50개 휴먼 보이스 생성
        from tools.audio.voice_presets_human_50 import VOICE_PRESETS_HUMAN_50
        device = "cpu" if "--cpu" in sys.argv else "mps"
        build_all(device=device, presets=VOICE_PRESETS_HUMAN_50, manifest_name="voice_library_human_50.json")
    else:
        device = "mps"
        if "--cpu" in sys.argv:
            device = "cpu"
        build_all(device=device)
