"""Tests for the Korean Bert-VITS2 training pipeline helpers
(tools/_bert_vits2_kr/train_korean.py) — filelist building + KO config gen."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools._bert_vits2_kr.train_korean import build_ko_config, build_raw_filelist  # noqa: E402


def test_build_raw_filelist(tmp_path):
    audios = tmp_path / "audios"
    audios.mkdir()
    (audios / "a.wav").write_bytes(b"RIFF")
    (audios / "b.wav").write_bytes(b"RIFF")
    (audios / "noise.mp3").write_bytes(b"x")  # no transcript entry -> skipped
    transcript = tmp_path / "transcript.txt"
    transcript.write_text("a 여호와는 나의 목자니\na 여호와는 나의 목자니\nb 네 마음을 다하여\n", encoding="utf-8")

    raw = build_raw_filelist(audios, transcript, tmp_path, "spk")
    lines = raw.read_text(encoding="utf-8").splitlines()
    # 'a' duplicated in transcript -> dict keeps last; noise has no transcript -> skipped
    assert len(lines) == 2  # a, b
    assert all("|spk|KO|" in l for l in lines)
    assert any(l.startswith(str((tmp_path / "audios" / "raw" / "a.wav"))) for l in lines)


def test_build_ko_config(tmp_path):
    template = PROJECT_ROOT / "tools" / "_bert_vits2_kr" / "configs" / "config.json"
    cfg = build_ko_config(template, tmp_path, "test_spk")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data["data"]["n_speakers"] == 1
    assert data["data"]["spk2id"] == {"test_spk": 0}
    assert data["data"]["sampling_rate"] == 44100
    assert data["data"]["cleaned_text"] is True
    assert (tmp_path / "config.json").exists()
