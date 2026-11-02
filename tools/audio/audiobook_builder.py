"""Audiobook factory tool: EPUB/TXT/MD -> multi-voice, chaptered audiobook.

Actions the `audiobook` pipeline stages call:

- ``parse``         book file -> ``lines`` (speaker/kind/section/emotion per line)
- ``design_anchor`` English voice description -> reusable voice anchor WAV
- ``synthesize``    lines + cast anchors -> verified per-line WAVs (VoxCPM clone,
                    Whisper round-trip check, best-of-N, resumable)
- ``assemble``      per-line WAVs -> gapped, loudness-normalised ``.m4b`` (with
                    chapter markers) and ``.mp3``
"""

from __future__ import annotations

import difflib
import json
import re
import shutil
import subprocess
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from posixpath import dirname, join, normpath
from typing import Any
from xml.etree import ElementTree as ET

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

WHISPER_REPO = "mlx-community/whisper-large-v3-turbo"
DEFAULT_EMOTION = {
    "h1": "차분하고 묵직한 나레이션",
    "h2": "또렷하고 안정적인 소제목 낭독",
    "p": "차분하고 자연스러운 나레이션",
}
SYSTEM_EMOTION = "차갑고 기계적인 시스템 안내 음성"
SYSTEM_PREFIXES = ("시스템 알림", "[시스템]", "【시스템】")
TAG_RE = re.compile(r"^\[([^\]\n]{1,20})\]\s*(.+)$", re.S)
SENT_RE = re.compile(r"(?<=[.!?。…])\s+")


# ---------------------------------------------------------------- parsing
class _Blocks(HTMLParser):
    """Collect h1-h3 / p text blocks from XHTML in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []
        self._tag: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h2", "h3", "p", "li", "blockquote"):
            self._tag, self._buf = tag, []

    def handle_data(self, data):
        if self._tag:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == self._tag:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                self.blocks.append((tag, text))
            self._tag = None


def read_blocks(path: Path) -> tuple[str, list[tuple[str, str]]]:
    """Return (title, [(tag, text)]) for .epub / .txt / .md."""
    suffix = path.suffix.lower()
    if suffix == ".epub":
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("META-INF/container.xml"))
            opf_path = root.find(".//{*}rootfile").attrib["full-path"]
            opf = ET.fromstring(z.read(opf_path))
            manifest = {i.attrib["id"]: i.attrib["href"] for i in opf.iterfind(".//{*}manifest/{*}item")}
            title_el = opf.find(".//{*}title")
            title = (title_el.text or "").strip() if title_el is not None else path.stem
            blocks: list[tuple[str, str]] = []
            for ref in opf.iterfind(".//{*}spine/{*}itemref"):
                href = manifest.get(ref.attrib["idref"])
                if not href or not href.endswith((".xhtml", ".html", ".htm")) or href.endswith("nav.xhtml"):
                    continue
                p = _Blocks()
                p.feed(z.read(normpath(join(dirname(opf_path), href))).decode("utf-8", "replace"))
                blocks += p.blocks
        return title, blocks
    if suffix in (".txt", ".md"):
        blocks, title = [], path.stem
        for para in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
            para = para.strip()
            if not para:
                continue
            m = re.match(r"^(#{1,3})\s+(.*)$", para)
            if m:
                blocks.append((f"h{len(m.group(1))}", m.group(2).strip()))
            else:
                blocks.append(("p", re.sub(r"\s+", " ", para)))
        return title, blocks
    raise ValueError(f"unsupported book format: {suffix} (use .epub, .txt, .md; convert PDF to text first)")


def chunk_text(text: str, limit: int = 120) -> list[str]:
    """Group sentences into chunks of about `limit` chars (VoxCPM stays stable on short spans)."""
    out, cur = [], ""
    for s in SENT_RE.split(text):
        if cur and len(cur) + len(s) + 1 > limit:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out


def parse_book(path: Path, chunk_limit: int = 120) -> dict[str, Any]:
    title, blocks = read_blocks(path)
    lines: list[dict[str, Any]] = []
    section = title
    for tag, text in blocks:
        if tag in ("h1", "h2", "h3"):
            kind = "h1" if tag == "h1" else "h2"
            if kind == "h2":
                section = text
            lines.append({"speaker": "narrator", "kind": kind, "section": text if kind == "h2" else title,
                          "text": text, "emotion": DEFAULT_EMOTION[kind]})
            continue
        speaker, body = "narrator", text
        if text.startswith(SYSTEM_PREFIXES):
            speaker = "system"
        else:
            m = TAG_RE.match(text)
            if m:
                speaker, body = m.group(1).strip(), m.group(2).strip()
        pieces = [body] if speaker == "system" else chunk_text(body, chunk_limit)
        for n, piece in enumerate(pieces):
            lines.append({"speaker": speaker, "kind": "p" if n == 0 else "c", "section": section, "text": piece,
                          "emotion": SYSTEM_EMOTION if speaker == "system" else DEFAULT_EMOTION["p"]})
    for i, ln in enumerate(lines):
        ln["i"] = i
    return {"version": "1.0", "title": title, "source": str(path), "lines": lines,
            "speakers": sorted({ln["speaker"] for ln in lines}),
            "total_chars": sum(len(ln["text"]) for ln in lines)}


# --------------------------------------------------------------- helpers
def _norm(s: str) -> str:
    return re.sub(r"[^0-9가-힣a-zA-Z]", "", s)


def _sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _dur(path: Path | str) -> float:
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)])
    return float(out.decode().strip())


def _ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def _transcribe(path: Path) -> str:
    import mlx_whisper

    return mlx_whisper.transcribe(str(path), path_or_hf_repo=WHISPER_REPO, language="ko")["text"].strip()


def _gap(prev: dict | None, cur: dict) -> float:
    """Seconds of silence inserted before `cur`."""
    if prev is None:
        return 0.0
    if cur["kind"] == "h2":
        return 1.0
    if prev["kind"] == "h2":
        return 0.6
    if "system" in (cur["speaker"], prev["speaker"]):
        return 0.5
    if cur["kind"] == "c":
        return 0.35
    return 0.7


class AudiobookBuilder(BaseTool):
    name = "audiobook_builder"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "audiobook"
    provider = "voxcpm"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg", "cmd:ffprobe"]
    install_instructions = "Needs ffmpeg, the VoxCPM2 env (see voxcpm_tts) and `mlx_whisper` for verification."
    agent_skills = ["voxcpm-tts", "tts-sample-unification"]
    capabilities = ["audiobook_parse", "audiobook_synthesize", "audiobook_assemble", "voice_anchor_design"]

    input_schema = {
        "type": "object",
        "required": ["action"],
        "properties": {
            "action": {"type": "string", "enum": ["parse", "design_anchor", "synthesize", "assemble"]},
            "book_path": {"type": "string", "description": "parse: .epub/.txt/.md source."},
            "chunk_limit": {"type": "integer", "default": 120},
            "lines_path": {"type": "string", "description": "synthesize/assemble: reviewed lines JSON."},
            "cast": {"type": "object", "description": "speaker -> anchor WAV path (synthesize)."},
            "work_dir": {"type": "string", "description": "Per-line WAVs and results.json live here."},
            "voice_design": {"type": "string", "description": "design_anchor: ENGLISH voice description."},
            "sample_text": {"type": "string", "description": "design_anchor: Korean text the anchor speaks."},
            "emotion": {"type": "string"},
            "output_path": {"type": "string"},
            "max_attempts": {"type": "integer", "default": 5},
            "accept_sim": {"type": "number", "default": 0.93},
            "title": {"type": "string"},
            "author": {"type": "string"},
            "target_lufs": {"type": "number", "default": -19.0},
            "bitrate": {"type": "string", "default": "96k"},
        },
    }
    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=6000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["action", "lines_path", "book_path"]
    side_effects = ["writes WAV/JSON/m4b/mp3 files under work_dir / output_path"]
    user_visible_verification = ["Listen to chapter starts, system lines and the lowest-similarity lines"]

    def get_status(self) -> ToolStatus:
        return ToolStatus.AVAILABLE if shutil.which("ffmpeg") else ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 25.0 if inputs.get("action") == "synthesize" else 5.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        handlers = {"parse": self._parse, "design_anchor": self._design_anchor,
                    "synthesize": self._synthesize, "assemble": self._assemble}
        handler = handlers.get(inputs.get("action"))
        if handler is None:
            return ToolResult(success=False, error=f"unknown action: {inputs.get('action')!r}")
        try:
            data = handler(inputs)
        except KeyError as e:
            return ToolResult(success=False, error=f"missing input: {e}")
        except (ValueError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as e:
            return ToolResult(success=False, error=str(e))
        return ToolResult(success=True, data=data, artifacts=data.get("artifacts", []),
                          duration_seconds=round(time.time() - start, 2))

    def _parse(self, inp: dict[str, Any]) -> dict[str, Any]:
        book = parse_book(Path(inp["book_path"]), inp.get("chunk_limit", 120))
        out = Path(inp.get("output_path", "audiobook_lines.json"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(book, ensure_ascii=False, indent=1), encoding="utf-8")
        return {"output": str(out), "lines": len(book["lines"]), "speakers": book["speakers"],
                "total_chars": book["total_chars"], "artifacts": [str(out)]}

    def _voxcpm(self):
        from tools.audio.voxcpm_tts import VoxCPMTTS

        return VoxCPMTTS()

    def _design_anchor(self, inp: dict[str, Any]) -> dict[str, Any]:
        out = Path(inp["output_path"])
        r = self._voxcpm().execute({"text": inp["sample_text"], "voice_design": inp["voice_design"],
                                    "emotion": inp.get("emotion", ""), "output_path": str(out)})
        if not r.success:
            raise RuntimeError(r.error)
        return {"output": str(out), "duration_seconds": r.data["duration_seconds"], "artifacts": [str(out)],
                "note": "Listen, then approve as the voice anchor. Re-run with a tweaked description if needed."}

    def _synthesize(self, inp: dict[str, Any]) -> dict[str, Any]:
        book = json.loads(Path(inp["lines_path"]).read_text(encoding="utf-8"))
        cast: dict[str, str] = inp["cast"]
        missing = sorted({ln["speaker"] for ln in book["lines"]} - set(cast))
        if missing:
            raise ValueError(f"no voice anchor in cast for speakers: {missing}")
        work = Path(inp["work_dir"])
        work.mkdir(parents=True, exist_ok=True)
        tts, attempts_max, accept = self._voxcpm(), inp.get("max_attempts", 5), inp.get("accept_sim", 0.93)
        results_path = work / "results.json"
        done = {r["i"]: r for r in json.loads(results_path.read_text())} if results_path.exists() else {}
        for ln in book["lines"]:
            i = ln["i"]
            final = work / f"{i:04d}_{ln['speaker']}.wav"
            if i in done and final.exists():
                continue
            best = None
            for a in range(attempts_max):
                tmp = work / f"{i:04d}_try{a}.wav"
                r = tts.execute({"text": ln["text"], "reference_audio": cast[ln["speaker"]],
                                 "emotion": ln.get("emotion", ""), "device": "mps", "output_path": str(tmp)})
                if not r.success:
                    continue
                hyp = _transcribe(tmp)
                sim, d = _sim(ln["text"], hyp), _dur(tmp)
                ratio = d / max(len(_norm(ln["text"])) * 0.17, 0.5)  # ~0.17 s per Korean syllable
                ok_len = 0.5 <= ratio <= 1.9
                score = sim if ok_len else sim - 0.5
                if best is None or score > best[0]:
                    best = (score, sim, hyp, d, a + 1, tmp)
                if sim >= accept and ok_len:
                    break
            if best is None:
                raise RuntimeError(f"line {i}: every attempt failed")
            shutil.copy(best[5], final)
            done[i] = {"i": i, "speaker": ln["speaker"], "kind": ln["kind"], "file": str(final),
                       "sim": round(best[1], 3), "attempts": best[4], "duration": round(best[3], 2), "hyp": best[2]}
            results_path.write_text(json.dumps(sorted(done.values(), key=lambda r: r["i"]),
                                               ensure_ascii=False, indent=1), encoding="utf-8")
            for t in work.glob(f"{i:04d}_try*.wav"):
                t.unlink()
        rows = sorted(done.values(), key=lambda r: r["i"])
        return {"results": str(results_path), "lines": len(rows),
                "weak_lines": [r["i"] for r in rows if r["sim"] < accept],
                "total_seconds": round(sum(r["duration"] for r in rows), 1), "artifacts": [str(results_path)]}

    def _assemble(self, inp: dict[str, Any]) -> dict[str, Any]:
        book = json.loads(Path(inp["lines_path"]).read_text(encoding="utf-8"))
        work = Path(inp["work_dir"])
        tmp = work / "_assemble"
        tmp.mkdir(parents=True, exist_ok=True)
        out_base = Path(inp["output_path"])
        out_base.parent.mkdir(parents=True, exist_ok=True)
        parts: list[Path] = []
        chapters: list[tuple[int, str]] = []
        t, prev = 0.0, None
        for ln in book["lines"]:
            wav = work / f"{ln['i']:04d}_{ln['speaker']}.wav"
            if not wav.exists():
                raise FileNotFoundError(f"missing synthesized line {wav.name}; run synthesize first")
            g = _gap(prev, ln)
            if g:
                sil = tmp / f"gap_{ln['i']}.wav"
                _ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(g), str(sil))
                parts.append(sil)
                t += g
            if ln["kind"] in ("h1", "h2"):
                chapters.append((int(t * 1000), ln["text"]))
            parts.append(wav)
            t += _dur(wav)
            prev = ln
        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts), encoding="utf-8")
        raw, norm = tmp / "raw.wav", tmp / "norm.wav"
        _ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-ar", "44100", "-ac", "1", str(raw))
        _ffmpeg("-i", str(raw), "-af", f"loudnorm=I={inp.get('target_lufs', -19.0)}:TP=-2:LRA=9",
                "-ar", "44100", str(norm))
        total_ms = int(_dur(norm) * 1000)
        title = inp.get("title") or book.get("title", "Audiobook")
        meta = f";FFMETADATA1\ntitle={title}\nartist={inp.get('author', '')}\nalbum={title}\n"
        for n, (s, name) in enumerate(chapters):
            e = chapters[n + 1][0] - 1 if n + 1 < len(chapters) else total_ms
            meta += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={s}\nEND={e}\ntitle={name}\n"
        meta_path = tmp / "meta.txt"
        meta_path.write_text(meta, encoding="utf-8")
        br = inp.get("bitrate", "96k")
        m4b, mp3 = out_base.with_suffix(".m4b"), out_base.with_suffix(".mp3")
        _ffmpeg("-i", str(norm), "-i", str(meta_path), "-map_metadata", "1", "-map_chapters", "1",
                "-c:a", "aac", "-b:a", br, str(m4b))
        _ffmpeg("-i", str(norm), "-i", str(meta_path), "-map_metadata", "1", "-c:a", "libmp3lame",
                "-b:a", br, str(mp3))
        return {"m4b": str(m4b), "mp3": str(mp3), "duration_seconds": round(total_ms / 1000, 1),
                "chapters": [{"start_seconds": round(s / 1000, 1), "title": n} for s, n in chapters],
                "artifacts": [str(m4b), str(mp3)]}
