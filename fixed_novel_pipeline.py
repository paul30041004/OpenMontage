import os
import json
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path("/Users/paul/Documents/OpenMontage")
SERIES_DIR = BASE_DIR / "projects/stranger-in-complex"
FONT_MYEONGJO = "/Users/paul/Library/Fonts/NanumMyeongjo-Bold.ttf"
FONT_GOTHIC = "/Users/paul/Library/Fonts/NanumGothic-Bold.ttf"

# 자연스럽고 명료한 낭독 속도 (자연스러운 기본 템포 +0%, 피치 -1Hz)
VOICE_ANCHOR = "ko-KR-InJoonNeural"
VOICE_RATE = "+0%"
VOICE_PITCH = "-1Hz"

ALL_EPISODES = [
    {
        "ep_num": 1,
        "ep_id": "ep001",
        "title": "104호의 우유 주머니",
        "scenes": [
            {
                "scene_id": "sc01_hook",
                "badge": "01. 새벽의 낯선 발소리",
                "text": "30년 동안 이 아파트에 살면서,\n나는 이웃들의 발자국 소리만 들어도 누구인지 알 수 있었습니다.\n하지만 그날 새벽의 소리는, 결코 이 단지의 것이 아니었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (190, 75, 75),
                "zoom": "in"
            },
            {
                "scene_id": "sc02_routine",
                "badge": "02. 10년간의 규칙적인 일과",
                "text": "매일 아침 6시 30분, 104호 김 영감님은\n문을 열고 우유를 들여놓곤 했습니다.\n지난 10년 동안, 단 하루도 거른 적이 없는 일과였습니다.",
                "lead_in": 0.3,
                "pause_after": 1.0,
                "accent": (160, 140, 100),
                "zoom": "out"
            },
            {
                "scene_id": "sc03_anomaly",
                "badge": "03. 뜯기지 않은 우유 주머니",
                "text": "그런데 오늘 아침, 104호 앞에는 우유 주머니 세 개가\n뜯기지도 않은 채 고스란히 걸려 있었습니다.\n그리고 문틈 사이로, 희미하지만 분명한 낯선 냄새가 풍겼습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (210, 120, 50),
                "zoom": "in"
            },
            {
                "scene_id": "sc04_cliffhanger",
                "badge": "04. [클리프행어] 안쪽에서 풀린 도어록",
                "text": "조심스레 다가가 문손잡이에 손이 닿았을 때였습니다.\n철컥.\n잠겨 있어야 할 문이 안쪽에서 스르륵 풀리며...\n아주 천천히 열리기 시작했습니다.",
                "lead_in": 0.4,
                "pause_after": 2.2,  # 클리프행어 여유 침묵
                "accent": (240, 40, 40),
                "zoom": "in_fast"
            },
            {
                "scene_id": "sc05_next",
                "badge": "05. 다음 화 예고",
                "text": "열린 문틈 사이로 마주친 그 눈빛은,\n104호 김 영감이 아니었습니다.\n제2화 〈그 남자의 신발장〉으로 이어집니다.",
                "lead_in": 0.3,
                "pause_after": 1.5,
                "accent": (180, 180, 180),
                "zoom": "out"
            }
        ]
    },
    {
        "ep_num": 2,
        "ep_id": "ep002",
        "title": "그 남자의 신발장",
        "scenes": [
            {
                "scene_id": "sc01_hook",
                "badge": "01. 어둠 속의 눈동자",
                "text": "열린 문틈으로 마주친 남자는 검은색 롱코트를 입고 있었습니다.\n그는 아무 말 없이 나를 빤히 응시하더니,\n천천히 문을 닫아걸었습니다. 쾅.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (210, 80, 80),
                "zoom": "in"
            },
            {
                "scene_id": "sc02_guard",
                "badge": "02. 경비실의 기이한 침묵",
                "text": "곧장 1층 경비실로 내려가 박 씨에게 104호 상황을 알렸습니다.\n하지만 늘 친절하던 박 씨의 얼굴이 딱딱하게 굳어지더니,\n'순자 씨, 104호 일엔 더 이상 신경 끄세요'라며 고개를 돌렸습니다.",
                "lead_in": 0.3,
                "pause_after": 1.0,
                "accent": (160, 140, 100),
                "zoom": "out"
            },
            {
                "scene_id": "sc03_discovery",
                "badge": "03. 분리수거장의 흔적",
                "text": "의아한 마음으로 돌아선 복도 끝 분리수거장.\n헌 옷 수거함 옆에 버려진 검은 쓰레기봉투 사이로,\n붉은 얼룩이 선명하게 묻은 가죽 장갑 한 짝이 떨어져 있었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (220, 110, 50),
                "zoom": "in"
            },
            {
                "scene_id": "sc04_cliffhanger",
                "badge": "04. [클리프행어] 떨어진 열쇠고리",
                "text": "장갑을 살펴보려 다가간 순간, 그 밑에서 낯익은 물건이 보였습니다.\n104호 김 영감님이 손녀에게 받았다며 늘 자랑하던...\n그 은색 나비 열쇠고리였습니다.",
                "lead_in": 0.4,
                "pause_after": 2.2,
                "accent": (240, 40, 40),
                "zoom": "in_fast"
            },
            {
                "scene_id": "sc05_next",
                "badge": "05. 다음 화 예고",
                "text": "이 장갑의 주인은 누구이며, 김 영감님은 어디로 사라진 것일까?\n제3화 〈지하 주차장의 번호판〉으로 이어집니다.",
                "lead_in": 0.3,
                "pause_after": 1.5,
                "accent": (180, 180, 180),
                "zoom": "out"
            }
        ]
    },
    {
        "ep_num": 3,
        "ep_id": "ep003",
        "title": "지하 주차장의 번호판",
        "scenes": [
            {
                "scene_id": "sc01_hook",
                "badge": "01. CCTV 사각지대",
                "text": "은색 나비 열쇠고리를 쥐고 지하 주차장으로 향했습니다.\n단지 내에서 가장 어둡고, CCTV가 닿지 않는 B3 구역 구석에\n먼지를 뒤집어쓴 검은 세단 한 대가 서 있었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (80, 150, 210),
                "zoom": "in"
            },
            {
                "scene_id": "sc02_trunk",
                "badge": "02. 트렁크 틈새의 옷자락",
                "text": "차량 번호판은 진흙으로 교묘하게 가려져 있었습니다.\n숨을 죽이고 차체 쪽으로 다가섰을 때,\n덜 닫힌 트렁크 틈새로 감색 모직 코트 자락이 끼어있는 것이 보였습니다.",
                "lead_in": 0.3,
                "pause_after": 1.0,
                "accent": (180, 140, 90),
                "zoom": "out"
            },
            {
                "scene_id": "sc03_ring",
                "badge": "03. 울리지 않는 전화",
                "text": "그 순간, 고요하던 주차장에 날카로운 진동음이 울렸습니다.\n내 주머니 속 휴대전화 화면에 뜬 발신자 이름.\n'104호 김 영감님'.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (230, 90, 50),
                "zoom": "in"
            },
            {
                "scene_id": "sc04_cliffhanger",
                "badge": "04. [클리프행어] 뒤에서 비친 헤드라이트",
                "text": "떨리는 손으로 통화 버튼을 누르려는 찰나,\n쿠웅- 지하 주차장 진입로에서 굉음과 함께\n강렬한 상향등 불빛이 내 등을 정면으로 비추기 시작했습니다.",
                "lead_in": 0.4,
                "pause_after": 2.2,
                "accent": (250, 30, 30),
                "zoom": "in_fast"
            },
            {
                "scene_id": "sc05_next",
                "badge": "05. 다음 화 예고",
                "text": "빛을 등지고 서서히 다가오는 차량의 실루엣.\n제4화 〈보건소 시절의 진료 기록〉으로 이어집니다.",
                "lead_in": 0.3,
                "pause_after": 1.5,
                "accent": (180, 180, 180),
                "zoom": "out"
            }
        ]
    },
    {
        "ep_num": 4,
        "ep_id": "ep004",
        "title": "보건소 시절의 진료 기록",
        "scenes": [
            {
                "scene_id": "sc01_hook",
                "badge": "01. 기적적인 탈출",
                "text": "헤드라이트 불빛을 피해 비상계단 문을 박차고 달아났습니다.\n숨을 헐떡이며 집에 들어와 문을 걸어 잠근 뒤,\n과거 15년 전 보건소 간호사 시절 보관해 둔 개인 수첩을 꺼냈습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (140, 190, 110),
                "zoom": "in"
            },
            {
                "scene_id": "sc02_notebook",
                "badge": "02. 15년 전의 환자 명단",
                "text": "그 수첩에는 당시 보건소 관내에서 일어났던\n의문의 실종 사건 피해자들과 특이 환자들의 기록이 적혀 있었습니다.\n그리고 104호 김 영감님의 과거 직업란에는...\n'구립 정신병원 특수관리동 책임자'라고 적혀 있었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.0,
                "accent": (160, 140, 100),
                "zoom": "out"
            },
            {
                "scene_id": "sc03_chief",
                "badge": "03. 새로 부임한 관리소장",
                "text": "더욱 소름 돋는 것은, 지난주 우리 단지에 새로 부임한 관리소장의 이름이\n당시 그 병원에서 사라졌던 유일한 장기 입원 환자의 이름과\n한 글자도 틀리지 않고 일치한다는 사실이었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (210, 110, 60),
                "zoom": "in"
            },
            {
                "scene_id": "sc04_cliffhanger",
                "badge": "04. [클리프행어] 현관 도어록 소리",
                "text": "그 진실을 깨달은 순간, 어두운 거실에 적막을 깨는 소리가 울렸습니다.\n삐- 삐- 삐- 삐-.\n누군가 우리 집 현관문 도어록 비밀번호를 누르고 있었습니다.",
                "lead_in": 0.4,
                "pause_after": 2.2,
                "accent": (240, 30, 30),
                "zoom": "in_fast"
            },
            {
                "scene_id": "sc05_next",
                "badge": "05. 다음 화 예고",
                "text": "우리 집 비밀번호를 알고 있는 그 자의 정체는?\n제5화 〈닫히지 않는 비상구 계단〉으로 이어집니다.",
                "lead_in": 0.3,
                "pause_after": 1.5,
                "accent": (180, 180, 180),
                "zoom": "out"
            }
        ]
    },
    {
        "ep_num": 5,
        "ep_id": "ep005",
        "title": "닫히지 않는 비상구 계단",
        "scenes": [
            {
                "scene_id": "sc01_hook",
                "badge": "01. 도어록의 마지막 번호",
                "text": "도어록의 마지막 번호가 눌리고, 띠리릭- 경쾌한 잠금 해제음이 울렸습니다.\n나는 부엌 식칼을 쥐고 벽 뒤로 몸을 숨겼습니다.\n현관문이 열리고, 천천히 안으로 들어서는 검은 구두의 발소리.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (220, 60, 60),
                "zoom": "in"
            },
            {
                "scene_id": "sc02_voice",
                "badge": "02. 불청객의 목소리",
                "text": "침입자는 거실 불을 켜지 않은 채 나지막이 읊조렸습니다.\n'순자 씨, 15년 전 보건소에서 그 차트를 보지 말았어야지.'\n그 목소리는 바로... 관리소장이었습니다.",
                "lead_in": 0.3,
                "pause_after": 1.0,
                "accent": (170, 130, 90),
                "zoom": "out"
            },
            {
                "scene_id": "sc03_escape",
                "badge": "03. 베란다 비상계단으로",
                "text": "소장이 거실로 진입하는 틈을 타,\n나는 베란다 비상 탈출 사다리를 타고 아래층으로 필사적으로 내려갔습니다.\n단지 밖으로 벗어나 경찰서로 가야만 했습니다.",
                "lead_in": 0.3,
                "pause_after": 1.2,
                "accent": (200, 120, 60),
                "zoom": "in"
            },
            {
                "scene_id": "sc04_cliffhanger",
                "badge": "04. [클리프행어] 단지 입구의 차단기",
                "text": "단지 정문에 도달했을 때, 모든 가로등이 일제히 소등되었습니다.\n그리고 굳게 닫힌 차단기 너머에서,\n경비원 박 씨와 낯선 사내 서넛이 손전등을 든 채 나를 둘러싸기 시작했습니다.",
                "lead_in": 0.4,
                "pause_after": 2.2,
                "accent": (250, 20, 20),
                "zoom": "in_fast"
            },
            {
                "scene_id": "sc05_next",
                "badge": "05. 시즌 1 파트 클라이맥스 예고",
                "text": "이 아파트 단지 전체가 거대한 함정이었다.\n제6화 〈이방인들의 연합〉에서 진실의 전모가 밝혀집니다.",
                "lead_in": 0.3,
                "pause_after": 1.5,
                "accent": (180, 180, 180),
                "zoom": "out"
            }
        ]
    }
]


def create_scene_card(ep_title: str, ep_num: int, scene_info: dict, output_path: Path):
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), (14, 18, 24))
    draw = ImageDraw.Draw(bg)

    for y in range(H):
        alpha = int((y / H) * 85)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    accent = scene_info["accent"]
    draw.line([(120, 120), (W - 120, 120)], fill=(60, 65, 75), width=2)
    draw.line([(120, H - 120), (W - 120, H - 120)], fill=(60, 65, 75), width=2)

    font_badge = ImageFont.truetype(FONT_GOTHIC, 28)
    font_title = ImageFont.truetype(FONT_MYEONGJO, 44)
    font_body = ImageFont.truetype(FONT_MYEONGJO, 54)
    font_footer = ImageFont.truetype(FONT_GOTHIC, 24)

    draw.text((120, 65), f"단지 내의 이방인  |  {ep_title}", fill=(170, 175, 185), font=font_badge)
    draw.text((W - 320, 65), f"제 {ep_num} 화", fill=accent, font=font_badge)
    draw.text((120, 160), scene_info["badge"], fill=accent, font=font_title)

    lines = scene_info["text"].split("\n")
    start_y = 380
    line_spacing = 88
    for i, line in enumerate(lines):
        draw.text((122, start_y + i * line_spacing + 2), line, fill=(0, 0, 0), font=font_body)
        draw.text((120, start_y + i * line_spacing), line, fill=(245, 245, 248), font=font_body)

    draw.text((120, H - 90), "OPENMONTAGE NOVEL-TO-VIDEO PIPELINE", fill=(90, 95, 105), font=font_footer)
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
    """
    Edge-TTS 생성 후 48000Hz stereo WAV로 변환하고,
    앞뒤 여유 버퍼(lead_in, pause_after)를 정확히 추가하여 음성이 절대 짤리지 않게 처리.
    """
    import edge_tts
    tmp_mp3 = output_wav.with_suffix(".tmp.mp3")
    
    # 쉼표 및 마침표에 자연스러운 호흡 여유 부여
    formatted_text = text.replace("\n", " ").strip()
    
    comm = edge_tts.Communicate(
        text=formatted_text,
        voice=VOICE_ANCHOR,
        rate=VOICE_RATE,
        pitch=VOICE_PITCH
    )
    await comm.save(str(tmp_mp3))

    # Lead-in (adelay ms) 및 Trailing silence (apad) 적용 + 48kHz Stereo WAV
    delay_ms = int(lead_in * 1000)
    af_filter = f"adelay={delay_ms}|{delay_ms},apad=pad_dur={pause_after}"

    cmd = [
        "ffmpeg", "-y", "-i", str(tmp_mp3),
        "-af", af_filter,
        "-ar", "48000", "-ac", "2",
        str(output_wav)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if tmp_mp3.exists():
        tmp_mp3.unlink()


def render_scene_video_clip(img_path: Path, audio_wav: Path, zoom_type: str, out_clip: Path):
    """
    씬 이미지와 씬 오디오를 결합하여 정확한 길이의 1080p MP4 클립 생성
    """
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


async def process_episode(ep: dict):
    ep_id = ep["ep_id"]
    ep_num = ep["ep_num"]
    ep_title = ep["title"]

    ep_dir = SERIES_DIR / ep_id
    audio_dir = ep_dir / "audio"
    visual_dir = ep_dir / "visuals"
    render_dir = ep_dir / "renders"
    for d in [audio_dir, visual_dir, render_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"🎬 [제 {ep_num} 화] 《{ep_title}》 정밀 싱크 렌더링 시작")
    print(f"=======================================================")

    scene_clips = []
    
    for idx, sc in enumerate(ep["scenes"], 1):
        sc_id = sc["scene_id"]
        print(f"  [{idx}/{len(ep['scenes'])}] {sc['badge']} 처리 중...")

        # 1. 고음질 WAV 오디오 렌더링 (여유 호흡 + 패딩 포함)
        audio_wav = audio_dir / f"{sc_id}.wav"
        await render_scene_audio(sc["text"], sc["lead_in"], sc["pause_after"], audio_wav)

        # 2. 고화질 비주얼 카드 생성
        img_png = visual_dir / f"{sc_id}.png"
        create_scene_card(ep_title, ep_num, sc, img_png)

        # 3. 싱크 완벽 일치 MP4 클립 렌더링
        clip_mp4 = render_dir / f"{sc_id}_clip.mp4"
        render_scene_video_clip(img_png, audio_wav, sc["zoom"], clip_mp4)
        scene_clips.append(clip_mp4)

    # 4. 씬 클립들 Concat 결합
    concat_txt = render_dir / "clips_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in scene_clips:
            f.write(f"file '{c.resolve()}'\n")

    raw_ep_video = ep_dir / f"{ep_id}_voice_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_txt),
        "-c", "copy",
        str(raw_ep_video)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 5. 서스펜스 BGM 생성 및 Auto-Ducking 믹싱
    ep_dur = get_duration(raw_ep_video)
    bgm_path = audio_dir / "bgm_suspense.wav"
    fade_out_st = max(0, ep_dur - 4)

    filter_complex_str = (
        f"[1:a]lowpass=f=350[noise];"
        f"[0:a][noise]amix=inputs=2[mix];"
        f"[mix]tremolo=f=0.25:d=0.35,aecho=0.8:0.7:800|1500:0.2|0.15,afade=t=in:ss=0:d=3,afade=t=out:st={fade_out_st:.1f}:d=4[out]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"aevalsrc=0.18*sin(2*PI*55*t)+0.09*sin(2*PI*65.4*t)+0.06*sin(2*PI*82.4*t):s=48000:d={ep_dur + 5:.1f}",
        "-f", "lavfi", "-i", f"anoisesrc=d={ep_dur + 5:.1f}:c=pink:r=48000:a=0.012",
        "-filter_complex", filter_complex_str,
        "-map", "[out]",
        "-ar", "48000", "-ac", "2",
        str(bgm_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 6. 최종 비디오 + 오디오 믹스 (Sidechain ducking)
    final_video = ep_dir / f"{ep_id}_final.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_ep_video),
        "-i", str(bgm_path),
        "-filter_complex",
        "[1:a]volume=0.32[bgm_base];"
        "[bgm_base][0:a]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=350[bgm_ducked];"
        "[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[mix];"
        "[mix]loudnorm=I=-16:TP=-1.5:LRA=11[norm]",
        "-map", "0:v",
        "-map", "[norm]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(final_video)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"✨ [성공] 제 {ep_num} 화 완료본 (총 {ep_dur:.1f}초, 음성 끊김 0%): {final_video}")


async def main():
    print("🚀 [전편 리마스터링] 자연스러운 호흡/속도 & 무결점 싱크 일괄 렌더링 시작...")
    for ep in ALL_EPISODES:
        await process_episode(ep)

    # 7. 전체 1화~5화 연속 통합본 재생성
    print("\n=======================================================")
    print("🎞️ [통합본 빌더] 제1화~제5화 몰아보기 마스터 비디오 최종 병합")
    print("=======================================================")
    
    all_episodes = [
        SERIES_DIR / "ep001/ep001_final.mp4",
        SERIES_DIR / "ep002/ep002_final.mp4",
        SERIES_DIR / "ep003/ep003_final.mp4",
        SERIES_DIR / "ep004/ep004_final.mp4",
        SERIES_DIR / "ep005/ep005_final.mp4",
    ]
    
    binge_concat_txt = SERIES_DIR / "binge_concat.txt"
    with open(binge_concat_txt, "w", encoding="utf-8") as f:
        for ep_file in all_episodes:
            if ep_file.exists():
                f.write(f"file '{ep_file.resolve()}'\n")

    binge_master_video = SERIES_DIR / "series_season1_binge_master.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(binge_concat_txt),
        "-c", "copy",
        str(binge_master_video)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    total_dur = get_duration(binge_master_video)
    print(f"\n🎉🎉 [완벽 해결] 전편 및 통합 몰아보기 완성 (총 {total_dur:.1f}초): {binge_master_video}")


if __name__ == "__main__":
    asyncio.run(main())
