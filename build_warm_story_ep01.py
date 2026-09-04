import os
import json
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path("/Users/paul/Documents/OpenMontage")
PROJECT_DIR = BASE_DIR / "projects/warm-life-stories/ep001"
AUDIO_DIR = PROJECT_DIR / "audio"
VISUAL_DIR = PROJECT_DIR / "visuals"
RENDER_DIR = PROJECT_DIR / "renders"

for d in [AUDIO_DIR, VISUAL_DIR, RENDER_DIR]:
    d.mkdir(parents=True, exist_ok=True)

FONT_MYEONGJO = "/Users/paul/Library/Fonts/NanumMyeongjo-Bold.ttf"
FONT_GOTHIC = "/Users/paul/Library/Fonts/NanumGothic-Bold.ttf"

# 따뜻하고 다정한 나레이션 톤
VOICE_ANCHOR = "ko-KR-InJoonNeural"
VOICE_RATE = "-2%"    # 살짝 더 차분하고 따뜻한 어조
VOICE_PITCH = "+0Hz"   # 온기 있는 표준 톤

EPISODE_DATA = {
    "title": "낡은 가죽 가방과 만 원짜리 세 장",
    "ep_num": 1,
    "scenes": [
        {
            "scene_id": "sc01_intro",
            "badge": "01. 지하철역 모퉁이의 작은 구두방",
            "text": "서울 변두리의 작은 지하철역 앞에는,\n30년째 비가 오나 눈이 오나 문을 여는 한 평 남짓한 구두방이 있습니다.\n그곳의 주인은 손마디가 까맣게 굳은 일흔둘의 만복 할아버지입니다.",
            "lead_in": 0.4,
            "pause_after": 1.4,
            "accent": (230, 170, 90),
            "zoom": "in"
        },
        {
            "scene_id": "sc02_boy",
            "badge": "02. 한겨울의 어린 손님",
            "text": "칼바람이 불던 어느 추운 겨울 저녁,\n초등학교 3학년쯤 되어 보이는 어린 소년 하나가\n다 떨어진 운동화를 들고 구두방 문을 조심스레 두드렸습니다.\n'할아버지... 이 신발 꿰매는 데 얼마예요? 제겐 삼천 원밖에 없는데요...'",
            "lead_in": 0.4,
            "pause_after": 1.2,
            "accent": (210, 150, 80),
            "zoom": "out"
        },
        {
            "scene_id": "sc03_secret",
            "badge": "03. 밑창에 숨겨진 만 원짜리 세 장",
            "text": "할아버지는 아무 말 없이 낡은 신발을 받아 들었습니다.\n가장 튼튼한 가죽을 덧대어 새 신발처럼 깨끗이 닦아낸 뒤,\n소년 몰래 신발 밑창 안쪽에 곱게 접은 만 원짜리 세 장과 쪽지 하나를 넣어두었습니다.\n'추운 날씨에 기죽지 마라. 씩씩하게 걸어라.'",
            "lead_in": 0.4,
            "pause_after": 1.5,
            "accent": (240, 160, 60),
            "zoom": "in"
        },
        {
            "scene_id": "sc04_reunion",
            "badge": "04. 20년 뒤, 찾아온 정장 차림의 신사",
            "text": "그리고 20년의 세월이 흐른 어느 날.\n초라한 구두방 앞에 말끔한 양복을 입은 청년이 찾아와\n만복 할아버지의 거친 손을 두 손으로 꼭 쥐며 눈물을 흘렸습니다.\n'할아버지... 20년 전 그 신발 덕분에, 제가 오늘 대학교수가 되었습니다.'",
            "lead_in": 0.4,
            "pause_after": 2.2,
            "accent": (235, 120, 70),
            "zoom": "in_fast"
        },
        {
            "scene_id": "sc05_closing",
            "badge": "05. 오늘의 따뜻한 한마디",
            "text": "누군가에게 베푼 작은 온기 하나가,\n한 사람의 인생 전체를 일으켜 세우는 기적이 됩니다.\n오늘 당신의 하루에도 따뜻한 위로와 축복이 가득하길 바랍니다.",
            "lead_in": 0.4,
            "pause_after": 1.8,
            "accent": (220, 190, 140),
            "zoom": "out"
        }
    ]
}


def create_warm_card(scene_info: dict, output_path: Path):
    W, H = 1920, 1080
    # Warm cozy background (Deep warm brown & amber tone)
    bg = Image.new("RGB", (W, H), (26, 20, 16))
    draw = ImageDraw.Draw(bg)

    # Warm Vignette gradient
    for y in range(H):
        alpha = int((y / H) * 60)
        draw.line([(0, y), (W, y)], fill=(10, 5, 2, alpha))

    accent = scene_info["accent"]
    # Elegant golden divider lines
    draw.line([(120, 120), (W - 120, 120)], fill=(90, 70, 50), width=2)
    draw.line([(120, H - 120), (W - 120, H - 120)], fill=(90, 70, 50), width=2)

    font_badge = ImageFont.truetype(FONT_GOTHIC, 28)
    font_title = ImageFont.truetype(FONT_MYEONGJO, 42)
    font_body = ImageFont.truetype(FONT_MYEONGJO, 52)
    font_footer = ImageFont.truetype(FONT_GOTHIC, 24)

    # Header
    draw.text((120, 65), "인생의 봄날은 언제나 오늘이어라  |  마음을 어루만지는 감동 실화", fill=(210, 190, 170), font=font_badge)
    draw.text((W - 380, 65), "제 1 화", fill=accent, font=font_badge)
    draw.text((120, 160), scene_info["badge"], fill=accent, font=font_title)

    # Body Text (High legibility warm ivory color)
    lines = scene_info["text"].split("\n")
    start_y = 380
    line_spacing = 88
    for i, line in enumerate(lines):
        # subtle soft shadow
        draw.text((122, start_y + i * line_spacing + 2), line, fill=(0, 0, 0), font=font_body)
        draw.text((120, start_y + i * line_spacing), line, fill=(250, 246, 240), font=font_body)

    draw.text((120, H - 90), "OPENMONTAGE WARM AUDIOBOOK SERIES", fill=(130, 110, 95), font=font_footer)
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
    print("📖 [감동 실화 오디오북 1화] 렌더링 시작...")
    scene_clips = []

    for idx, sc in enumerate(EPISODE_DATA["scenes"], 1):
        sc_id = sc["scene_id"]
        print(f"  [{idx}/{len(EPISODE_DATA['scenes'])}] {sc['badge']} 낭독 및 비주얼 생성 중...")

        # 1. 고품질 낭독 WAV
        audio_wav = AUDIO_DIR / f"{sc_id}.wav"
        await render_scene_audio(sc["text"], sc["lead_in"], sc["pause_after"], audio_wav)

        # 2. 웜톤 1080p 카드
        img_png = VISUAL_DIR / f"{sc_id}.png"
        create_warm_card(sc, img_png)

        # 3. Ken Burns 클립 렌더링
        clip_mp4 = RENDER_DIR / f"{sc_id}_clip.mp4"
        render_zoom_clip(img_png, audio_wav, sc["zoom"], clip_mp4)
        scene_clips.append(clip_mp4)

    # 4. 씬 결합
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

    # 5. 따뜻하고 서정적인 어쿠스틱 피아노/패드 BGM 생성 (Major Chords: C-G-Am-F 진행 느낌의 평화로운 선율)
    total_dur = get_duration(raw_video)
    bgm_path = AUDIO_DIR / "bgm_warm_piano.wav"
    fade_out_st = max(0, total_dur - 4)

    # C Major 따뜻한 배음 합성: C3(130.8Hz), E3(164.8Hz), G3(196Hz), C4(261.6Hz)
    synth_expr = (
        "0.12*sin(2*PI*130.8*t)+0.08*sin(2*PI*164.8*t)+0.07*sin(2*PI*196.0*t)+0.05*sin(2*PI*261.6*t*(1+0.005*sin(2*PI*0.3*t)))"
    )
    filter_complex_str = (
        f"[1:a]lowpass=f=250[noise];"
        f"[0:a][noise]amix=inputs=2[mix];"
        f"[mix]chorus=0.7:0.9:55:0.4:0.25:2,aecho=0.8:0.8:1000|1800:0.25|0.2,afade=t=in:ss=0:d=3,afade=t=out:st={fade_out_st:.1f}:d=4[out]"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"aevalsrc={synth_expr}:s=48000:d={total_dur + 5:.1f}",
        "-f", "lavfi", "-i", f"anoisesrc=d={total_dur + 5:.1f}:c=pink:r=48000:a=0.008",
        "-filter_complex", filter_complex_str,
        "-map", "[out]",
        "-ar", "48000", "-ac", "2",
        str(bgm_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 6. 최종 믹싱 및 렌더링 (Auto-Ducking & Volume Normalization)
    final_video = PROJECT_DIR / "ep01_warm_story_final.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(bgm_path),
        "-filter_complex",
        "[1:a]volume=0.28[bgm_base];"
        "[bgm_base][0:a]sidechaincompress=threshold=0.04:ratio=5:attack=30:release=400[bgm_ducked];"
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
    print(f"\n✨🎉 [완성] 감동 오디오북 제1화 렌더링 완료 (총 {dur_final:.1f}초): {final_video}")


if __name__ == "__main__":
    asyncio.run(main())
