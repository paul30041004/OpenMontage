import os
import json
import asyncio
import subprocess
from pathlib import Path

# ==========================================
# 1. 제1화 에피소드 대본 데이터 (JSON)
# ==========================================
EPISODE_SCRIPT = [
    {
        "scene_id": "ep01_sc01",
        "section": "cold_open_hook",
        "text": "30년 동안 이 아파트에 살면서, 나는 이웃들의 발자국 소리만 들어도 누구인지 알 수 있었습니다. 하지만... 그날 새벽에 들린 그 소리는, 결코 이 단지의 소리가 아니었습니다.",
        "pause_after": 1.2
    },
    {
        "scene_id": "ep01_sc02",
        "section": "daily_exposition",
        "text": "매일 아침 6시 30분. 104호의 김 영감님은 문을 열고 배달된 우유를 들여놓곤 했습니다. 지난 10년 동안, 단 하루도 거른 적이 없는 규칙적인 일과였지요.",
        "pause_after": 0.8
    },
    {
        "scene_id": "ep01_sc03",
        "section": "rising_tension",
        "text": "그런데 오늘 아침, 104호 앞에는 우유 주머니 세 개가 뜯기지도 않은 채 고스란히 걸려 있었습니다. 그리고 문틈 사이로, 희미하지만 분명하게 풍겨오는... 낯선 냄새가 코를 찔렀습니다.",
        "pause_after": 1.0
    },
    {
        "scene_id": "ep01_sc04",
        "section": "cliffhanger_climax",
        "text": "조심스레 다가가 초인종을 누르려던 내 손이, 문손잡이에 닿았을 때였습니다. 철컥. 잠겨 있어야 할 도어록이, 안쪽에서 스르륵 풀리며... 문이 아주 천천히 열리기 시작했습니다.",
        "pause_after": 2.0  # 클리프행어 직전의 긴 침묵
    },
    {
        "scene_id": "ep01_sc05",
        "section": "outro_preview",
        "text": "열린 문틈 사이로 마주친 그 눈빛은, 104호 김 영감이 아니었습니다. 제2화, '그 남자의 신발장'으로 이어집니다.",
        "pause_after": 0.5
    }
]

# ==========================================
# 2. 앵커 보이스 설정 (시니어 스릴러 최적화)
# ==========================================
VOICE_ANCHOR = "ko-KR-InJoonNeural"
VOICE_RATE = "-6%"     # 시니어가 듣기 편안한 살짝 여유 있는 템포
VOICE_PITCH = "-2Hz"   # 서스펜스 분위기를 위한 중저음 피치

BASE_DIR = Path("/Users/paul/Documents/OpenMontage")
OUTPUT_DIR = BASE_DIR / "projects/stranger-in-complex/ep001/audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def generate_scene_audio(scene_id: str, text: str, output_path: Path):
    """Edge-TTS를 이용한 단일 씬 오디오 생성"""
    import edge_tts
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE_ANCHOR,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH
    )
    await communicate.save(str(output_path))


def create_silence_clip(duration_sec: float, output_path: Path):
    """FFmpeg를 사용해 정확한 길이의 무음(Pause) 클립 생성"""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", str(duration_sec),
        "-q:a", "9", "-acodec", "libmp3lame",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


async def build_episode():
    print(f"🎬 [에피소드 1화] 오디오 렌더링 시작...")
    print(f"🎙️ 고정 앵커 보이스: {VOICE_ANCHOR} (Rate: {VOICE_RATE}, Pitch: {VOICE_PITCH})")
    
    file_list_txt = OUTPUT_DIR / "concat_list.txt"
    concat_lines = []

    for idx, scene in enumerate(EPISODE_SCRIPT, 1):
        scene_id = scene["scene_id"]
        text = scene["text"]
        pause = scene.get("pause_after", 0.5)

        # 1. 씬 나레이션 생성
        scene_file = OUTPUT_DIR / f"{scene_id}.mp3"
        print(f"  [{idx}/{len(EPISODE_SCRIPT)}] {scene['section']} 생성 중...")
        await generate_scene_audio(scene_id, text, scene_file)
        concat_lines.append(f"file '{scene_file.resolve()}'")

        # 2. 씬 뒤에 들어갈 휴지기(Silence) 생성
        if pause > 0:
            silence_file = OUTPUT_DIR / f"{scene_id}_pause.mp3"
            create_silence_clip(pause, silence_file)
            concat_lines.append(f"file '{silence_file.resolve()}'")

    # 3. FFmpeg Concat 파일 작성
    with open(file_list_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_lines))

    # 4. 전체 에피소드 단일 오디오 파일 병합
    final_output = OUTPUT_DIR.parent / "ep01_voice_master.mp3"
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(file_list_txt),
        "-c", "copy",
        str(final_output)
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    print(f"\n✅ 1화 보이스 마스터 완성: {final_output}")


if __name__ == "__main__":
    asyncio.run(build_episode())
