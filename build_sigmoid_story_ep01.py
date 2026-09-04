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

for d in [AUDIO_DIR, VISUAL_DIR, RENDER_DIR]:
    d.mkdir(parents=True, exist_ok=True)

FONT_MYEONGJO = "/Users/paul/Library/Fonts/NanumMyeongjo-Bold.ttf"
FONT_GOTHIC = "/Users/paul/Library/Fonts/NanumGothic-Bold.ttf"

VOICE_ANCHOR = "ko-KR-InJoonNeural"
VOICE_RATE = "+0%"
VOICE_PITCH = "-1Hz"

EPISODE_DATA = {
    "title": "매일 밤 도어록을 누르던 노인의 비밀",
    "ep_num": 1,
    "scenes": [
        {
            "scene_id": "sc01_suspense_intro",
            "badge": "01. 새벽 2시의 불길한 도어록 소리",
            "phase": "suspense",
            "text": "3주 전부터, 매일 새벽 2시만 되면 소름 끼치는 일이 반복되었습니다.\n삐- 삐- 삐- 삐-.\n누군가 우리 집 현관문 비밀번호를 누르고, 문손잡이를 거칠게 덜컥거리는 소리였습니다.",
            "lead_in": 0.4,
            "pause_after": 1.2,
            "bg_color": (16, 18, 24),
            "accent": (220, 60, 60),
            "zoom": "in"
        },
        {
            "scene_id": "sc02_cctv_horror",
            "badge": "02. CCTV에 찍힌 앞집 노인의 섬뜩한 눈빛",
            "phase": "suspense",
            "text": "공포에 떨며 설치한 현관 CCTV를 확인한 순간, 심장이 얼어붙었습니다.\n그 사람은 바로 앞집에 혼자 사는 일흔여덟의 박 노인이었습니다.\n초점 없는 눈으로 우리 집 문손잡이를 부여잡고 무언가를 중얼거리고 있었습니다.",
            "lead_in": 0.3,
            "pause_after": 1.2,
            "bg_color": (20, 16, 18),
            "accent": (230, 80, 50),
            "zoom": "out"
        },
        {
            "scene_id": "sc03_cliffhanger_confront",
            "badge": "03. [클라이맥스] 마침내 열린 문과 몽둥이",
            "phase": "suspense",
            "text": "참다못해 경찰에 신고하려던 그날 밤, 띠리릭- 잠금장치가 풀리며 문이 벌컥 열렸습니다.\n문 앞에는 손에 굵은 나무 막대기를 쥔 노인이 서 있었고,\n나는 비명을 지르며 바닥으로 주저앉았습니다.",
            "lead_in": 0.4,
            "pause_after": 2.2,  # 시그모이드 변곡점 (긴 침묵)
            "bg_color": (12, 12, 16),
            "accent": (255, 40, 40),
            "zoom": "in_fast"
        },
        {
            "scene_id": "sc04_sigmoid_reversal",
            "badge": "04. [반전] '아가씨, 제발 나와! 불이야!'",
            "phase": "reversal_touching",
            "text": "하지만 노인은 나를 해치려던 것이 아니었습니다.\n'아가씨! 가스 냄새가 나! 어서 피해!'\n노인은 몽둥이로 환풍구를 깨부수며 가스에 질식해 쓰러져가던 나를 들쳐업고 계단을 내달렸습니다.",
            "lead_in": 0.4,
            "pause_after": 1.5,
            "bg_color": (28, 22, 16),
            "accent": (240, 160, 60),
            "zoom": "in"
        },
        {
            "scene_id": "sc05_heartwarming_truth",
            "badge": "05. 3주간의 눈물겨운 진실",
            "text": "알고 보니 보일러 배관이 헐거워져 3주 전부터 미세한 가스가 새고 있었고,\n후각이 예민했던 노인은 문을 열어 나를 깨우려 밤마다 사투를 벌였던 것이었습니다.\n가장 무서웠던 이웃은, 나를 살리기 위해 목숨을 걸었던 수호천사였습니다.",
            "lead_in": 0.4,
            "pause_after": 2.0,
            "bg_color": (32, 24, 18),
            "accent": (230, 190, 120),
            "zoom": "out"
        }
    ]
}


def create_scene_card(scene_info: dict, output_path: Path):
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), scene_info["bg_color"])
    draw = ImageDraw.Draw(bg)

    for y in range(H):
        alpha = int((y / H) * 75)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    accent = scene_info["accent"]
    draw.line([(120, 120), (W - 120, 120)], fill=(70, 60, 50), width=2)
    draw.line([(120, H - 120), (W - 120, H - 120)], fill=(70, 60, 50), width=2)

    font_badge = ImageFont.truetype(FONT_GOTHIC, 28)
    font_title = ImageFont.truetype(FONT_MYEONGJO, 44)
    font_body = ImageFont.truetype(FONT_MYEONGJO, 54)
    font_footer = ImageFont.truetype(FONT_GOTHIC, 24)

    draw.text((120, 65), "반전 실화 극장  |  오해와 진실의 시그모이드 드라마", fill=(190, 180, 170), font=font_badge)
    draw.text((W - 380, 65), "제 1 화", fill=accent, font=font_badge)
    draw.text((120, 160), scene_info["badge"], fill=accent, font=font_title)

    lines = scene_info["text"].split("\n")
    start_y = 380
    line_spacing = 88
    for i, line in enumerate(lines):
        draw.text((122, start_y + i * line_spacing + 2), line, fill=(0, 0, 0), font=font_body)
        draw.text((120, start_y + i * line_spacing), line, fill=(248, 246, 242), font=font_body)

    draw.text((120, H - 90), "OPENMONTAGE SUSPENSE-HUMAN PIPELINE", fill=(110, 100, 90), font=font_footer)
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
        z_expr = "min(zoom+0.0006,1.15)"
    elif zoom_type == "in_fast":
        z_expr = "min(zoom+0.0012,1.25)"
    else:
        z_expr = "max(1.15-0.0006*on,1.0)"

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
    print("🔥 [시그모이드 반전 스릴러-감동 실화 1화] 제작 시작...")
    scene_clips = []

    for idx, sc in enumerate(EPISODE_DATA["scenes"], 1):
        sc_id = sc["scene_id"]
        print(f"  [{idx}/{len(EPISODE_DATA['scenes'])}] {sc['badge']} 렌더링 중...")

        audio_wav = AUDIO_DIR / f"{sc_id}.wav"
        await render_scene_audio(sc["text"], sc["lead_in"], sc["pause_after"], audio_wav)

        img_png = VISUAL_DIR / f"{sc_id}.png"
        create_scene_card(sc, img_png)

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

    # =========================================================================
    # 다이내믹 사운드트랙:
    # 1~3씬(전반부 ~60초): 다크 서스펜스 앰비언트 (55Hz Cello Drone)
    # 4~5씬(후반부 ~): 따뜻한 메이저 피아노 감동 선율로 교차 전환 (Crossfade)
    # =========================================================================
    total_dur = get_duration(raw_video)
    bgm_path = AUDIO_DIR / "bgm_sigmoid_dynamic.wav"
    split_time = 55.0  # 반전 시점

    # 1. Suspense BGM (앞부분)
    suspense_expr = "0.18*sin(2*PI*55*t)+0.09*sin(2*PI*65.4*t)+0.05*sin(2*PI*82.4*t)"
    # 2. Warm Piano BGM (뒷부분)
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

    # 3. 비디오 + 다이내믹 BGM Auto-Ducking 합성
    final_video = PROJECT_DIR / "ep01_sigmoid_thriller_final.mp4"
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
    print(f"\n🎉🎉 [완벽 제작] 시그모이드 반전 스릴러-감동 실화 1화 완성 (총 {dur_final:.1f}초): {final_video}")


if __name__ == "__main__":
    asyncio.run(main())
