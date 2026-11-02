"""Contracts for the audiobook factory: parsing, speaker tagging, chunking, assembly."""

import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from lib.pipeline_loader import load_pipeline
from tools.audio.audiobook_builder import AudiobookBuilder, chunk_text, parse_book

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body>
<h1>제일장 시험</h1>
<h2>첫 절</h2>
<p>첫 문단입니다. 두 번째 문장입니다.</p>
<p>시스템 알림: 레벨이 올랐습니다.</p>
<h2>둘째 절</h2>
<p>[시안] 나는 여기 있다.</p>
</body></html>"""


def _make_epub(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("META-INF/container.xml",
                   '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                   '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                   "</rootfiles></container>")
        z.writestr("OEBPS/content.opf",
                   '<package xmlns="http://www.idpf.org/2007/opf"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
                   "<dc:title>시험책</dc:title></metadata><manifest>"
                   '<item id="c1" href="c1.xhtml" media-type="application/xhtml+xml"/></manifest>'
                   '<spine><itemref idref="c1"/></spine></package>')
        z.writestr("OEBPS/c1.xhtml", XHTML)


def test_parse_epub_kinds_and_speakers(tmp_path: Path) -> None:
    book = tmp_path / "t.epub"
    _make_epub(book)
    parsed = parse_book(book)
    assert parsed["title"] == "시험책"
    assert [ln["kind"] for ln in parsed["lines"]] == ["h1", "h2", "p", "p", "h2", "p"]
    assert [ln["i"] for ln in parsed["lines"]] == list(range(6))
    assert parsed["speakers"] == ["narrator", "system", "시안"]
    assert parsed["lines"][4]["section"] == "둘째 절"
    assert parsed["lines"][5]["text"] == "나는 여기 있다."


def test_chunk_text_groups_sentences_without_splitting_them() -> None:
    text = " ".join(["가나다라마바사아자차."] * 30)
    chunks = chunk_text(text, 60)
    assert all(len(c) <= 60 for c in chunks)
    assert " ".join(chunks) == text


def test_unsupported_format_is_rejected(tmp_path: Path) -> None:
    f = tmp_path / "x.pdf"
    f.write_bytes(b"%PDF")
    result = AudiobookBuilder().execute({"action": "parse", "book_path": str(f), "output_path": str(tmp_path / "o.json")})
    assert not result.success and "unsupported" in result.error


def test_synthesize_requires_anchor_for_every_speaker(tmp_path: Path) -> None:
    lines = tmp_path / "lines.json"
    lines.write_text(json.dumps({"lines": [{"i": 0, "speaker": "narrator", "kind": "p", "text": "가", "emotion": ""}]}))
    result = AudiobookBuilder().execute({"action": "synthesize", "lines_path": str(lines), "cast": {},
                                         "work_dir": str(tmp_path / "w")})
    assert not result.success and "narrator" in result.error


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg required")
def test_assemble_writes_chaptered_m4b(tmp_path: Path) -> None:
    lines = [{"i": 0, "speaker": "narrator", "kind": "h1", "text": "제목"},
             {"i": 1, "speaker": "narrator", "kind": "h2", "text": "절 하나"},
             {"i": 2, "speaker": "narrator", "kind": "p", "text": "본문"},
             {"i": 3, "speaker": "narrator", "kind": "h2", "text": "절 둘"}]
    work = tmp_path / "w"
    work.mkdir()
    for ln in lines:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=220:d=1",
                        "-ar", "44100", "-ac", "1", str(work / f"{ln['i']:04d}_narrator.wav")], check=True)
    lp = tmp_path / "lines.json"
    lp.write_text(json.dumps({"title": "시험", "lines": lines}))
    result = AudiobookBuilder().execute({"action": "assemble", "lines_path": str(lp), "work_dir": str(work),
                                         "output_path": str(tmp_path / "out" / "book")})
    assert result.success, result.error
    assert [c["title"] for c in result.data["chapters"]] == ["제목", "절 하나", "절 둘"]
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_chapters", "-of", "json",
                                     result.data["m4b"]])
    assert len(json.loads(probe)["chapters"]) == 3
    assert Path(result.data["mp3"]).exists()


def test_pipeline_manifest_declares_audiobook_stages() -> None:
    manifest = load_pipeline("audiobook")
    assert [s["name"] for s in manifest["stages"]] == ["idea", "script", "assets", "compose", "publish"]
