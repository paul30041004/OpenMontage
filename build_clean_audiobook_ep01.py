import os
import json
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path("/Users/paul/Documents/OpenMontage")
PROJECT_DIR = BASE_DIR / "projects/suspense-human-stories/ep001"
AUDIO_DIR = PROJECT_DIR / "audio"
VISUAL_DIR = PROJECT_DIR / "visuals"
RENDER_DIR = PROJECT_DIR / "renders"

FONT_MYEONGJO = "/Users/paul/Library/Fonts/NanumMyeongjo-Bold.ttf"
FONT_GOTHIC = "/Users/paul/Library/Fonts/NanumGothic-Bold.ttf"

VOICE_ANCHOR = "ko-KR-InJoonNeural"
VOICE_RATE = "+0%"
VOICE_PITCH = "-1Hz"

# 시청자 몰입을 위해 모든 제작용 태그([클라이맥스], [반전] 등)를 완벽히 숨긴 순수 소설 챕터 구조
EPISODE_DATA = {
    "title": "밤마다 문을 두드리던 노인",
    "scenes": [
        {
            "scene_id": "sc01_intro",
            "chapter": "제 1 장.  새벽 2시의 불길한 소음",
            "text": "3주 전부터, 매일 새벽 2시만 되면 소름 끼치는 일이 반복되었습니다.\n삐- 삐- 삐- 삐-.\n누군가 우리 집 현관문 비밀번호를 누르고, 문손잡이를 거칠게 덜컥거리는 소리였습니다.",
            "lead_in": 0.4,
            "pause_after": 1.2,
            "bg_color": (16, 18, 24),
            "accent": (210, 180, 140),
            "zoom": "in"
        },
        {
            "scene_id": "sc02_cctv",
            "chapter": "제 2 장.  CCTV에 비친 그림자",
            "text": "공포에 떨며 설치한 현관 CCTV를 확인한 순간, 심장이 얼어붙었습니다.\n그 사람은 바로 앞집에 혼자 사는 일흔여덟의 박 노인이었습니다.\n초점 없는 눈으로 우리 집 문손잡이를 부여잡고 무언가를 중얼거리고 있었습니다.",
            "lead_in": 0.3,
            "pause_after": 1.2,
            "bg_color": (18, 18, 22),
            "accent": (210, 180, 140),
            "zoom": "out"
        },
        {
            "scene_id": "sc03_confront",
            "chapter": "제 3 장.  열려버린 현관문",
            "text": "참다못해 경찰에 신고하려던 그날 밤, 띠리릭- 잠금장치가 풀리며 문이 벌컥 열렸습니다.\n문 앞에는 손에 굵은 나무 막대기를 쥔 노인이 서 있었고,\n나는 비명을 지르며 바닥으로 주저앉았습니다.",
            "lead_in": 0.4,
            "pause_after": 2.2,  # 극적 정적
            "bg_color": (14, 14, 18),
            "accent": (210, 180, 140),
            "zoom": "in_fast"
        },
        {
            "scene_id": "sc04_reversal",
            "chapter": "제 4 장.  어둠 속에서 건넨 외침",
            "text": "하지만 노인은 나를 해치려던 것이 아니었습니다.\n'아가씨! 가스 냄새가 나! 어서 피해!'\n노인은 몽둥이로 환풍구를 깨부수며 가스에 질식해 쓰러져가던 나를 들쳐업고 계단을 내달렸습니다.",
            "lead_in": 0.4,
            "pause_after": 1.5,
            "bg_color": (26, 22, 18),
            "accent": (230, 190, 130),
            "zoom": "in"
        },
        {
            "scene_id": "sc05_truth",
            "chapter": "제 5 장.  가장 고마운 이웃",
            "text": "알고 보니 보일러 배관이 헐거워져 3주 전부터 미세한 가스가 새고 있었고,\n후각이 예민했던 노인은 문을 열어 나를 깨우려 밤마다 사투를 벌였던 것이었습니다.\n가장 무서웠던 이웃은, 나를 살리기 위해 목숨을 걸었던 수호천사였습니다.",
            "lead_in": 0.4,
            "pause_after": 2.0,
            "bg_color": (28, 22, 18),
            "accent": (230, 190, 130),
            "zoom": "out"
        }
    ]
}


def create_clean_scene_card(scene_info: dict, output_path: Path):
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), scene_info["bg_color"])
    draw = ImageDraw.Draw(bg)

    # 부드러운 비네팅
    for y in range(H):
        alpha = int((y / H) * 65)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    accent = scene_info["accent"]
    # 고급스러운 책/오디오북 레이아웃 라인
    draw.line([(140, 130), (W - 140, 130)], fill=(65, 60, 55), width=1)
    draw.line([(140, H - 130), (W - 140, H - 130)], fill=(65, 60, 55), width=1)

    font_top = ImageFont.truetype(FONT_GOTHIC, 24)
    font_chapter = ImageFont.truetype(FONT_MYEONGJO, 38)
    font_body = ImageFont.truetype(FONT_MYEONGJO, 54)

    # 상단: 깔끔한 소설 타이틀
    draw.text((140, 80), "감동 실화 오디오북  |  밤마다 문을 두드리던 노인", fill=(170, 165, 155), font=font_top)

    # 챕터 제목 (스포일러 없는 서정적 표현)
    draw.text((140, 175), scene_info["chapter"], fill=accent, font=font_chapter)

    # 본문 스토리 (시니어 최적화 명조 대형 자막)
    lines = scene_info["text"].split("\n")
    start_y = 390
    line_spacing = 90
    for i, line in enumerate(lines):
        draw.text((142, start_y + i * line_spacing + 2), line, fill=(0, 0, 0), font=font_body)
        draw.text((140, start_y + i * line_spacing), line, fill=(248, 246, 242), font=font_body)

    bg.save(output_path, "PNG")


def get_duration(p: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(p)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


async def render_scene_audio(text: str, lead_in: float, pause_after: float, output_wav: Path):
    import edge_tts
    tmp_mp3 = output_wav.with_suffix(".tmp.mp3")
    formatted_text = text.replace("\n", " ").strip()
    
    comm = edge_tts.Communicate(
        text=formatted_text,
        voice=VOICE_ANCHOR,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH
    )
    await comm.save(str(tmp_mp3))

    delay_ms = int(lead_in * 1000)
    af_filter = f"adelay={delay_ms}|{delay_ms},apad=pad_dur={pause_after}"

    subprocess.run([
        "ffmpeg", "-y", "-i", str(tmp_mp3),
        "-af", af_filter,
        "-ar", "48000", "-ac", "2",
        str(output_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if tmp_mp3.exists():
        tmp_mp3.unlink()


def render_zoom_clip(img_path: Path, audio_wav: Path, zoom_type: str, out_clip: Path):
    dur = get_duration(audio_wav)
    fps = 30
    total_frames = int(dur * fps)

    if zoom_type == "in":
        z_expr = "min(zoom+0.0005,1.12)"
    elif zoom_type == "in_fast":
        z_expr = "min(zoom+0.0010,1.20)"
    else:
        z_expr = "max(1.12-0.0005*on,1.0)"

    x_expr = "iw/2-(iw/zoom/2)"
    y_expr = "ih/2-(ih/zoom/2)"

    filter_str = (
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s=1920x1080:fps={fps},"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-i", str(audio_wav),
        "-vf", filter_str,
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_clip)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


async def main():
    print("✨ [깔끔한 자연스러운 낭독형 비디오] 렌더링 시작...")
    scene_clips = []

    for idx, sc in enumerate(EPISODE_DATA["scenes"], 1):
        sc_id = sc["scene_id"]
        print(f"  [{idx}/{len(EPISODE_DATA['scenes'])}] {sc['chapter']} 카드 및 영상 렌더링...")

        audio_wav = AUDIO_DIR / f"{sc_id}.wav"
        await render_scene_audio(sc["text"], sc["lead_in"], sc["pause_after"], audio_wav)

        img_png = VISUAL_DIR / f"{sc_id}.png"
        create_clean_scene_card(sc, img_png)

        clip_mp4 = RENDER_DIR / f"{sc_id}_clip.mp4"
        render_zoom_clip(img_png, audio_wav, sc["zoom"], clip_mp4)
        scene_clips.append(clip_mp4)

    concat_txt = RENDER_DIR / "clips_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in scene_clips:
            f.write(f"file '{c.resolve()}'\n")

    raw_video = PROJECT_DIR / "ep01_raw.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy",
        str(raw_video)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 서스펜스 ➔ 감동 피아노 다이내믹 크로스페이드 BGM
    total_dur = get_duration(raw_video)
    bgm_path = AUDIO_DIR / "bgm_clean.wav"
    split_time = 55.0

    suspense_expr = "0.18*sin(2*PI*55*t)+0.09*sin(2*PI*65.4*t)+0.05*sin(2*PI*82.4*t)"
    warm_expr = "0.12*sin(2*PI*130.8*t)+0.09*sin(2*PI*164.8*t)+0.07*sin(2*PI*196.0*t)+0.05*sin(2*PI*261.6*t)"

    filter_complex = (
        f"[0:a]afade=t=in:ss=0:d=2,afade=t=out:st={split_time - 2}:d=4[susp];"
        f"[1:a]afade=t=in:ss={split_time - 2}:d=4,afade=t=out:st={total_dur - 3}:d=3[warm];"
        f"[susp][warm]amix=inputs=2[bgm_mix];"
        f"[bgm_mix]chorus=0.6:0.8:50:0.3:0.25:2[out]"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"aevalsrc={suspense_expr}:s=48000:d={total_dur + 5:.1f}",
        "-f", "lavfi", "-i", f"aevalsrc={warm_expr}:s=48000:d={total_dur + 5:.1f}",
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ar", "48000", "-ac", "2",
        str(bgm_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 최종 병합 (Auto-Ducking)
    final_video = PROJECT_DIR / "ep01_clean_audiobook_final.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(bgm_path),
        "-filter_complex",
        "[1:a]volume=0.30[bgm_base];"
        "[bgm_base][0:a]sidechaincompress=threshold=0.04:ratio=6:attack=25:release=350[bgm_ducked];"
        "[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[mix];"
        "[mix]loudnorm=I=-16:TP=-1.5:LRA=11[norm]",
        "-map", "0:v",
        "-map", "[norm]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_video)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    dur_final = get_duration(final_video)
    print(f"\n🎉🎉 [완성] 시청자용 순수 오디오북 비디오 렌더링 완료 (총 {dur_final:.1f}초): {final_video}")


if __name__ == "__main__":
    asyncio.run(main())
