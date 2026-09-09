"""Emotion Tag Parser & Router for Korean TTS Engines.

Extracts inline emotion annotations (e.g. '[분노]', '(긴박하게)', '[e스포츠 캐스터]')
from raw script text, cleans the dialogue so brackets are not spoken aloud,
and translates cues into optimized instruction prompts for VoxCPM2, Qwen3-TTS, etc.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Tuple

# Pre-tuned natural language acting prompts for Korean emotional TTS
EMOTION_PRESETS: Dict[str, str] = {
    "분노": "분노에 차서 거칠고 강하게 쏘아붙이듯",
    "화남": "억누른 분노로 날카롭고 차갑게",
    "긴박": "숨이 차오르듯 빠르고 다급하며 긴장감 넘치게",
    "다급": "위험을 알리듯 매우 빠르고 긴박하게",
    "차분": "잔잔하고 차분하며 신뢰감 있는 목소리로",
    "따뜻": "따뜻하고 다정하게 감싸 안아주듯",
    "슬픔": "울먹이며 목소리가 떨리는 애절하고 비통한 톤으로",
    "눈물": "눈물을 참으며 말을 잇지 못하듯 슬프게",
    "기쁨": "밝고 경쾌하게 미소를 띤 목소리로",
    "환희": "벅차오르는 감격과 기쁨으로 가득 찬 톤으로",
    "e스포츠": "열정적인 e스포츠 캐스터 중계 톤으로, 빠르고 힘있게",
    "캐스터": "스포츠 경기 클라이맥스를 중계하듯 박진감 넘치게",
    "장엄": "무게감 있고 엄숙한 역사 다큐멘터리 나레이션 톤으로",
    "속삭임": "가까이에서 조용히 귓속말하듯 속삭이며",
    "냉소": "냉소적이고 비웃는 듯 차가운 어조로",
    "공포": "두려움에 떨며 겁에 질린 목소리로"
}


def parse_and_route_emotion(raw_text: str, default_emotion: Optional[str] = None) -> Tuple[str, str]:
    """
    Parses inline emotion markup, cleans dialogue, and returns (cleaned_text, emotion_prompt).

    Example:
        '[분노] 네가 어떻게 그럴 수가 있어!' ->
        ('네가 어떻게 그럴 수가 있어!', '분노에 차서 거칠고 강하게 쏘아붙이듯')
    """
    if not raw_text:
        return "", default_emotion or "자연스럽고 또렷하게"

    extracted_cue = None

    # Match leading or embedded [bracketed] or (parenthesized) emotion tags
    bracket_match = re.search(r"^[\[\(（【]([^\]\)）】]+)[\]\)）】]\s*", raw_text)
    if bracket_match:
        extracted_cue = bracket_match.group(1).strip()
        # Remove the tag from the spoken dialogue
        cleaned_text = raw_text[bracket_match.end():].strip()
    else:
        # Check anywhere in the text if someone wrote [감정]
        inline_match = re.search(r"[\[\(（【]([^\]\)）】]+)[\]\)）】]", raw_text)
        if inline_match:
            candidate = inline_match.group(1).strip()
            # Verify if candidate matches an emotion keyword
            if any(k in candidate for k in EMOTION_PRESETS.keys()):
                extracted_cue = candidate
                cleaned_text = (raw_text[:inline_match.start()] + " " + raw_text[inline_match.end():]).strip()
            else:
                cleaned_text = raw_text.strip()
        else:
            cleaned_text = raw_text.strip()

    # Determine final emotion instruction
    final_emotion = default_emotion or "자연스럽고 또렷한 나레이션 톤으로"
    if extracted_cue:
        # Check against presets
        matched_preset = None
        for key, prompt in EMOTION_PRESETS.items():
            if key in extracted_cue:
                matched_preset = prompt
                break
        if matched_preset:
            final_emotion = matched_preset
        else:
            # If user provided custom string (e.g. '비장하게 결의를 다지며'), use it directly
            final_emotion = extracted_cue

    return cleaned_text, final_emotion


if __name__ == "__main__":
    examples = [
        "[분노] 네가 어떻게 아벨을 죽일 수 있단 말이냐!",
        "(긴박하게) 지금 당장 성문 밖으로 대피해야 합니다!",
        "[e스포츠 캐스터] 마지막 한 타! 카인의 펀치가 정확히 적중합니다!",
        "[차분하고 따뜻하게] 힘들면 잠시 쉬어가도 괜찮아요.",
        "일반적인 설명 대본입니다."
    ]
    for ex in examples:
        txt, emo = parse_and_route_emotion(ex)
        print(f"INPUT: {ex}")
        print(f"TEXT : {txt}")
        print(f"EMO  : {emo}\n")
