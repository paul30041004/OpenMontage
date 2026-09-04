import os
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path("/Users/paul/Documents/OpenMontage")
EP_DIR = BASE_DIR / "projects/stranger-in-complex/ep001"
IMG_DIR = EP_DIR / "visuals"
IMG_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR = EP_DIR / "audio"
RENDER_DIR = EP_DIR / "renders"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

FONT_MYEONGJO = "/Users/paul/Library/Fonts/NanumMyeongjo-Bold.ttf"
FONT_GOTHIC = "/Users/paul/Library/Fonts/NanumGothic-Bold.ttf"

SCENE_META = [
    {
        "scene_id": "ep01_sc01",
        "title": "01. 새벽의 낯선 발소리",
        "bg_color": (15, 20, 28),
        "accent": (190, 75, 75),
        "text": "30년 동안 이 아파트에 살면서,\n나는 이웃들의 발자국 소리만 들어도 누구인지 알 수 있었습니다.\n하지만 그날 새벽의 소리는, 결코 이 단지의 것이 아니었습니다.",
        "zoom": "in"
    },
    {
        "scene_id": "ep01_sc02",
        "title": "02. 10년간의 규칙적인 일과",
        "bg_color": (22, 26, 32),
        "accent": (160, 140, 100),
        "text": "매일 아침 6시 30분, 104호 김 영감님은\n문을 열고 우유를 들여놓곤 했습니다.\n지난 10년 동안, 단 하루도 거른 적이 없는 일과였습니다.",
        "zoom": "out"
    },
    {
        "scene_id": "ep01_sc03",
        "title": "03. 뜯기지 않은 우유 주머니",
        "bg_color": (24, 20, 20),
        "accent": (210, 120, 50),
        "text": "오늘 아침, 우유 주머니 세 개가 고스란히 걸려 있었습니다.\n그리고 문틈 사이로, 희미하지만 분명하게 풍겨오는...\n낯선 냄새가 코를 찔렀습니다.",
        "zoom": "in"
    },
    {
        "scene_id": "ep01_sc04",
        "title": "04. [클리프행어] 안쪽에서 풀린 도어록",
        "bg_color": (10, 10, 14),
        "accent": (230, 45, 45),
        "text": "조심스레 다가가 문손잡이에 손이 닿았을 때였습니다.\n철컥.\n잠겨 있어야 할 문이 안쪽에서 스르륵 풀리며...\n아주 천천히 열리기 시작했습니다.",
        "zoom": "in_fast"
    },
    {
        "scene_id": "ep01_sc05",
        "title": "05. 다음 화 예고",
        "bg_color": (18, 18, 22),
        "accent": (180, 180, 180),
        "text": "열린 문틈 사이로 마주친 그 눈빛은,\n104호 김 영감이 아니었습니다.\n\n제2화 〈그 남자의 신발장〉으로 이어집니다.",
        "zoom": "out"
    }
]


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def create_scene_card(scene_info: dict, output_path: Path):
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), scene_info["bg_color"])
    draw = ImageDraw.Draw(bg)

    # Gradient Vignette overlay
    for y in range(H):
        alpha = int((y / H) * 80)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Decorative cinematic borders / grid lines
    accent = scene_info["accent"]
    draw.line([(120, 120), (W - 120, 120)], fill=(60, 65, 75), width=2)
    draw.line([(120, H - 120), (W - 120, H - 120)], fill=(60, 65, 75), width=2)

    # Load Fonts
    font_badge = ImageFont.truetype(FONT_GOTHIC, 28)
    font_title = ImageFont.truetype(FONT_MYEONGJO, 44)
    font_body = ImageFont.truetype(FONT_MYEONGJO, 56)
    font_footer = ImageFont.truetype(FONT_GOTHIC, 24)

    # Top Header
    draw.text((120, 65), "단지 내의 이방인  |  일상 미스터리 스릴러", fill=(170, 175, 185), font=font_badge)
    draw.text((W - 320, 65), "제 1 화", fill=accent, font=font_badge)

    # Scene Subject
    draw.text((120, 160), scene_info["title"], fill=accent, font=font_title)

    # Large Story Text (Senior optimized high-legibility centered block)
    lines = scene_info["text"].split("\n")
    start_y = 380
    line_spacing = 90
    for i, line in enumerate(lines):
        # Draw shadow
        draw.text((122, start_y + i * line_spacing + 2), line, fill=(0, 0, 0), font=font_body)
        draw.text((120, start_y + i * line_spacing), line, fill=(245, 245, 248), font=font_body)

    # Bottom watermark
    draw.text((120, H - 90), "OPENMONTAGE NOVEL-TO-VIDEO PIPELINE", fill=(90, 95, 105), font=font_footer)

    bg.save(output_path, "PNG")


def render_scene_clip(img_path: Path, duration: float, zoom_type: str, out_video: Path):
    fps = 30
    total_frames = int(duration * fps)

    if zoom_type == "in":
        z_expr = "min(zoom+0.0006,1.15)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif zoom_type == "in_fast":
        z_expr = "min(zoom+0.0012,1.25)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    else:  # out
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
        "-vf", filter_str,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p",
        str(out_video)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def main():
    print("🎨 [Step 2] 시각 에셋 생성 및 비디오 렌더링 시작...")
    
    scene_clips = []
    
    for idx, scene in enumerate(SCENE_META, 1):
        scene_id = scene["scene_id"]
        
        # 1. 씬 이미지 생성
        img_file = IMG_DIR / f"{scene_id}.png"
        create_scene_card(scene, img_file)
        
        # 2. 씬 오디오 길이 계산 (나레이션 + pause)
        audio_file = AUDIO_DIR / f"{scene_id}.mp3"
        pause_file = AUDIO_DIR / f"{scene_id}_pause.mp3"
        
        dur = get_audio_duration(audio_file)
        if pause_file.exists():
            dur += get_audio_duration(pause_file)
            
        print(f"  [{idx}/{len(SCENE_META)}] {scene['title']} ({dur:.2f}s) 렌더링 중...")
        
        # 3. Ken Burns 씬 클립 렌더링
        clip_file = RENDER_DIR / f"{scene_id}_clip.mp4"
        render_scene_clip(img_file, dur, scene["zoom"], clip_file)
        scene_clips.append(clip_file)

    # 4. 씬 클립들 Concat 리스트 작성
    concat_txt = RENDER_DIR / "clips_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for clip in scene_clips:
            f.write(f"file '{clip.resolve()}'\n")

    # 5. 영상과 Step 1에서 믹싱된 최종 오디오(ep01_final_audio.mp3) 결합
    final_video = EP_DIR / "ep01_final.mp4"
    mixed_audio = EP_DIR / "ep01_final_audio.mp3"

    print("🎬 최종 오디오 트랙과 영상 합성 중...")
    combine_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-i", str(mixed_audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_video)
    ]
    subprocess.run(combine_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"\n🎉 [완료] 제1화 완성본: {final_video}")


if __name__ == "__main__":
    main()
