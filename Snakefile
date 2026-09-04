# Long-form episode pipeline — resumable, chunk-aware, multi-ratio (OpenMontage).
# Usage:  snakemake --cores 1 projects/series-batch/E01/episode_9x16.mp4
#         snakemake --cores 1 --keep-going all_episodes
#
# Every episode is rendered in three ratios simultaneously:
#   16:9 (1280x720, series standard -> episode.mp4)
#    9:16 (720x1280, vertical shorts   -> episode_9x16.mp4)
#    4:3  (1280x960, classic           -> episode_4x3.mp4)

import json
from pathlib import Path

LUT = "assets/luts/redthread_book.cube"
BGM = "projects/book-proverbs-3/assets/music/bgm.mp3"
FONT = "NanumGothic"
ROOT = Path.cwd()

RATIOS = {"16:9": (1280, 720), "9:16": (720, 1280), "4:3": (1280, 960)}
RID = {"16:9": "16x9", "9:16": "9x16", "4:3": "4x3"}

EPISODES = json.loads(Path("projects/series-batch/episodes.json").read_text(encoding="utf-8"))


def ep(ep_id):
    return next(e for e in EPISODES if e["id"] == ep_id)


def bg_for(ratio):
    return f"projects/series-batch/shared/book_bg_{RID[ratio]}.mp4"


def ratio_of(rid):
    return next(r for r in RATIOS if RID[r] == rid)


def narration_sentences(e):
    """Split the episode's original scripture narration into sentences (the accurate 대본)."""
    import re
    text = e["narration"].strip()
    parts = re.split(r"(?<=[.!?。])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def show_face(eid):
    """Face (rhubarb lip-sync avatar) is OPTIONAL — off by default."""
    return bool(ep(eid).get("show_face", False))


def avatar_input(wildcards):
    return "projects/series-batch/{eid}/work/avatar.mp4".format(eid=wildcards.eid) if show_face(wildcards.eid) else []


rule all_episodes:
    input:
        expand("projects/series-batch/{eid}/episode_{rid}.mp4",
               eid=[e["id"] for e in EPISODES], rid=RID.values())


rule episode_alias:
    """Keep the historical name episode.mp4 = the 16:9 master."""
    input: "projects/series-batch/{eid}/episode_16x9.mp4"
    output: "projects/series-batch/{eid}/episode.mp4"
    shell:
        "cp {input} {output}"


rule tts:
    output: "projects/series-batch/{eid}/audio/narration.wav"
    run:
        e = ep(wildcards.eid)
        import subprocess, sys
        subprocess.run([sys.executable, "-c", f"""
from tools.audio.voxcpm_tts import VoxCPMTTS
r = VoxCPMTTS().execute({{
    'text': r'{e["narration"]}',
    'emotion': r'{e.get("emotion", "")}',
    'output_path': r'{output[0]}',
    'device': 'mps',
}})
assert r.success, r.error
"""], cwd=str(ROOT), check=True)


rule normalize:
    input: "projects/series-batch/{eid}/audio/narration.wav"
    output: "projects/series-batch/{eid}/audio/narration_norm.wav"
    shell:
        "sox {input} {output} gain -n norm -16"


rule subtitle:
    input: "projects/series-batch/{eid}/audio/narration_norm.wav"
    output: "projects/series-batch/{eid}/work/subs_precise.srt"
    run:
        import subprocess, sys, json
        e = ep(wildcards.eid)
        script = narration_sentences(e)
        script_json = json.dumps(script, ensure_ascii=False)
        subprocess.run([sys.executable, "-c", f"""
import json
from tools.subtitle.subtitle_from_audio import SubtitleFromAudio
r = SubtitleFromAudio().execute({{
    'audio_path': r'{input[0]}',
    'output_path': r'{output[0]}',
    'script_lines': json.loads(r'''{script_json}'''),
    'model_size': 'small', 'language': 'ko',
    'offset_seconds': 0.0,
}})
assert r.success, r.error
"""], cwd=str(ROOT), check=True)


rule karaoke:
    input: "projects/series-batch/{eid}/audio/narration_norm.wav"
    output: "projects/series-batch/{eid}/work/karaoke_{rid}.ass"
    params:
        w=lambda w: RATIOS[ratio_of(w.rid)][0],
        h=lambda w: RATIOS[ratio_of(w.rid)][1],
    run:
        import subprocess, sys, json
        e = ep(wildcards.eid)
        script = narration_sentences(e)
        script_json = json.dumps(script, ensure_ascii=False)
        subprocess.run([sys.executable, "-c", f"""
import json
from tools.subtitle.karaoke_subtitle import KaraokeSubtitle
r = KaraokeSubtitle().execute({{
    'audio_path': r'{input[0]}',
    'output_path': r'{output[0]}',
    'script_lines': json.loads(r'''{script_json}'''),
    'model_size': 'small', 'language': 'ko',
    'play_w': {params.w}, 'play_h': {params.h},
}})
assert r.success, r.error
"""], cwd=str(ROOT), check=True)


rule avatar:
    input: "projects/series-batch/{eid}/audio/narration_norm.wav"
    output: "projects/series-batch/{eid}/work/avatar.mp4"
    run:
        import subprocess, sys
        subprocess.run([sys.executable, "-c", f"""
from tools.avatar.rhubarb_lipsync import RhubarbLipsync
r = RhubarbLipsync().execute({{
    'audio_path': r'{input[0]}',
    'output_path': r'{output[0]}',
    'bg_path': r'{bg_for("16:9")}',
    'fps': 24,
}})
assert r.success, r.error
"""], cwd=str(ROOT), check=True)


rule composite:
    input: avatar = lambda w: avatar_input(w),
           narration = "projects/series-batch/{eid}/audio/narration_norm.wav",
           subs = "projects/series-batch/{eid}/work/karaoke_{rid}.ass"
    output: "projects/series-batch/{eid}/work/episode_raw_{rid}.mp4"
    params:
        bg=lambda w: bg_for(ratio_of(w.rid)),
        s=lambda w: RATIOS[ratio_of(w.rid)][1] / 720.0,   # font/margin scale
        ws=lambda w: RATIOS[ratio_of(w.rid)][0] / 1280.0, # x-position scale
    run:
        e = ep(wildcards.eid)
        import subprocess
        subs = str(input.subs)
        book_t = e["book"].replace(":", "\\:")
        title_t = e["title"].replace(":", "\\:")
        fs_book = int(round(52 * params.s))
        fs_title = int(round(40 * params.s))
        y_book = int(round(56 * params.s))
        y_title = int(round(116 * params.s))
        x0 = int(round(60 * params.ws))
        base_video = str(input.avatar) if show_face(wildcards.eid) else None
        bg_path = params.bg
        loop = [] if base_video else ["-stream_loop", "-1"]
        if base_video:
            vinput = base_video
        else:
            vinput = bg_path
        subprocess.run([
            "ffmpeg", "-y", *loop, "-i", vinput, "-i", str(input.narration), "-i", str(BGM),
            "-filter_complex",
            f"[0:v]drawtext=font={FONT}:text='{book_t}':fontsize={fs_book}:fontcolor=0x2B2620:borderw=2:bordercolor=white@0.9:x={x0}:y={y_book},"
            f"drawtext=font={FONT}:text='{title_t}':fontsize={fs_title}:fontcolor=0xB3352E:borderw=2:bordercolor=white@0.9:x={x0}:y={y_title},"
            f"ass={subs}[v];"
            f"[1:a]afade=t=in:st=0:d=0.3[an];"
            f"[2:a]atrim=0:12.5,afade=t=in:st=0:d=1.5,afade=t=out:st=10.5:d=2,volume=0.22[bgm];"
            f"[an][bgm]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", str(output)], check=True)


rule chunk:
    input: "projects/series-batch/{eid}/work/episode_raw_{rid}.mp4"
    output: "projects/series-batch/{eid}/episode_{rid}.mp4"
    run:
        import subprocess, sys
        subprocess.run([sys.executable, "-c", f"""
from tools.video.chunk_render import ChunkRender
r = ChunkRender().execute({{
    'video_path': r'{input[0]}',
    'output_path': r'{output[0]}',
    'chunk_seconds': 30,
    'lut': r'{LUT}',
}})
assert r.success, r.error
"""], cwd=str(ROOT), check=True)
