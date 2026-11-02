#!/usr/bin/env python3
"""build_audio.py — reads content.json, produces out/timing.json + out/audio.wav.
No LLM needed. Optional narration via edge-tts (free) or local VoxCPM2.
Usage: python build_audio.py [content.json] [outdir]
"""
import sys, os, json, math, subprocess, asyncio, wave
import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = sys.argv[1] if len(sys.argv) > 1 else "content.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
os.makedirs(OUT, exist_ok=True)
VO = os.path.join(OUT, "vo"); os.makedirs(VO, exist_ok=True)

content = json.load(open(CONTENT))
meta = content.get("meta", {})
shots = content["shots"]
aud = content.get("audio", {})
fps = meta.get("fps", 24)
# env overrides (handy for quick silent test renders): TTS=none/edge/voxcpm, SCORE=false
if os.environ.get("TTS"): aud["tts"] = os.environ["TTS"]
if os.environ.get("SCORE"): aud["score"] = os.environ["SCORE"].lower() != "false"

def decode(path):
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",path,"-f","s16le","-ac","1","-ar",str(SR),"pipe:1"])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0

def dur(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path]).strip())

def edge_tts(text, out, voice, rate):
    import edge_tts
    asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(out))

def voxcpm_tts(text, out, a, reference=None):
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from tools.tool_registry import registry
    registry.discover()
    tool = registry._tools["voxcpm_tts"]
    params = {"text": text, "device": a.get("device","mps"), "output_path": out}
    if reference: params["reference_audio"] = reference
    else: params["voice_design"] = a.get("voiceDesign","")
    if a.get("emotion"): params["emotion"] = a["emotion"]
    r = tool.execute(params)
    if not r.success: raise RuntimeError(getattr(r, "error", "voxcpm failed"))

def atempo(src, dst, factor):
    if abs(factor-1.0) < 1e-3:
        subprocess.check_call(["ffmpeg","-y","-i",src,"-c","copy",dst]); return
    subprocess.check_call(["ffmpeg","-y","-i",src,"-af",f"atempo={factor}",dst])

# ---- per-shot durations + voice files ----
tts = aud.get("tts", "edge")
rate = aud.get("rate", "+0%")
voice_name = aud.get("voice", "en-US-GuyNeural")
pad = aud.get("pad", 0.4)
lead = aud.get("lead", 0.15)
min_dur = meta.get("minShot", 2.2)
atempo = aud.get("atempo", 1.0)

shot_durs = []; voice_files = []
use_voice = tts != "none" and any(s.get("narration") for s in shots)
anchor = None; anchor_i = None
if use_voice and tts == "voxcpm":
    anchor_i = next(i for i, s in enumerate(shots) if s.get("narration"))
    anchor = os.path.join(VO, "anchor.wav")
    voxcpm_tts(shots[anchor_i]["narration"], anchor, aud)
    print("voxcpm anchor:", anchor, "-> cloning the rest")
for i, s in enumerate(shots):
    if use_voice and s.get("narration"):
        ext = "mp3" if tts == "edge" else "wav"
        raw = os.path.join(VO, f"vo_{i+1:02d}.{ext}")
        if tts == "edge": edge_tts(s["narration"], raw, voice_name, rate)
        elif tts == "voxcpm":
            if i == anchor_i: raw = anchor
            else: voxcpm_tts(s["narration"], raw, aud, reference=anchor)
        else: raise SystemExit(f"unknown tts: {tts}")
        proc = os.path.join(VO, f"vo_{i+1:02d}_t.wav")
        atempo(raw, proc, atempo if tts == "voxcpm" else 1.0)
        d = dur(proc); voice_files.append(proc)
        shot_durs.append(max(round((d + pad)*fps)/fps, min_dur))
        print(f"  shot {i+1:02d}: voice {d:5.2f}s -> {shot_durs[-1]:5.2f}s  {s['narration'][:34]}")
    else:
        voice_files.append(None)
        shot_durs.append(s.get("dur", 3.0))

starts = []; a = 0.0
for d in shot_durs: starts.append(round(a, 3)); a += d
TOTAL = round(a, 3)
json.dump({"shot": shot_durs, "starts": starts, "total": TOTAL}, open(os.path.join(OUT, "timing.json"), "w"))
print(f"timeline: {TOTAL:.2f}s, {len(shots)} shots")

# ---- assemble audio ----
want_score = aud.get("score", True) and any(voice_files) or aud.get("score_always", False)
if not any(voice_files) and not aud.get("score", True):
    print("no narration, score disabled -> silent"); sys.exit(0)

n = int(TOTAL * SR); t = np.arange(n)/SR
rng = np.random.default_rng(7)
voice = np.zeros(n)
for i, f in enumerate(voice_files):
    if not f: continue
    s = decode(f); i0 = int((starts[i] + lead)*SR); L = min(len(s), n-i0); voice[i0:i0+L] += s[:L]

score = np.zeros(n)
if aud.get("score", True):
    lfo = 0.5 + 0.5*np.sin(2*np.pi*0.08*t)
    bed = (0.05*np.sin(2*np.pi*55*t)+0.035*np.sin(2*np.pi*82.5*t)+0.02*np.sin(2*np.pi*110*t))*(0.6+0.4*lfo)
    padn = rng.normal(0,1,n); acc=0.0; lp=np.zeros(n)
    for i in range(n): acc += 0.003*(padn[i]-acc); lp[i]=acc
    lp = lp/(np.max(np.abs(lp))+1e-9); bed += 0.05*lp*(0.5+0.5*lfo)
    bed *= np.minimum(1,t/1.0)*np.minimum(1,(TOTAL-t)/1.2)
    score += bed
    for idx, s0 in enumerate(starts):
        i0=int(s0*SR); L=min(int(0.28*SR), n-i0); tt=np.arange(L)/SR; env=np.exp(-tt*22)
        amp = 0.30 if idx in (0, len(starts)-1) else 0.16
        score[i0:i0+L] += amp*env*np.sin(2*np.pi*(70-30*tt/0.28)*tt) + 0.08*np.exp(-tt*90)*rng.normal(0,1,L)
    i0=int(starts[-1]*SR); L=min(int(3*SR), n-i0); tt=np.arange(L)/SR
    freq=220+110*np.minimum(tt/1.5,1); phase=2*np.pi*np.cumsum(freq)/SR
    envl=np.minimum(tt/0.4,1)*np.exp(-tt*0.35)
    score[i0:i0+L] += 0.16*envl*np.sin(phase) + 0.08*np.exp(-tt*1.2)*np.sin(2*np.pi*660*tt)

if any(voice_files):
    env = np.abs(voice); win=int(0.12*SR); k=np.ones(win)/win
    sm = np.convolve(env,k,mode='same'); sm = sm/(np.max(sm)+1e-9)
    score *= (1.0 - 0.75*np.minimum(1.0, sm*3.0))

mix = voice + score*0.9
mix = np.tanh(mix*1.25)*0.9
mix = mix/(np.max(np.abs(mix))+1e-9)*0.94
with wave.open(os.path.join(OUT, "audio.wav"), "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix,mix],axis=1)*32767).astype(np.int16).tobytes())
print("wrote", os.path.join(OUT, "audio.wav"))
