"""Bert-VITS2 multilingual TTS tool for OpenMontage.

Wraps the fishaudio/Bert-VITS2 v2.3 multilingual model (ZH/EN/JP) plus a
Korean→Japanese pronunciation substitution path (`ko_to_kana`) so Korean text
can also be synthesized through the JP pipeline. Fully local — no API key.

Model + inference deps live under `tools/_bert_vits2/` (see
`skills/bert-vits2-tts.md` for setup). The tool shells out to a dedicated venv
so it never pollutes the OpenMontage runtime env.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from tools.audio.ko_to_kana import hangul_to_hiragana
from tools.base_tool import (
    BaseTool,
    DependencyError,
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

REPO_DIR = Path(__file__).resolve().parent.parent / "_bert_vits2"
VENV_PY = REPO_DIR / "venv" / "bin" / "python"
RUNNER = REPO_DIR / "run_infer.py"
DEFAULT_MODEL_DIR = REPO_DIR / "pretrained" / "v2.3"
DEFAULT_CONFIG = DEFAULT_MODEL_DIR / "config.json"

# Korean-native engine (jwj7140/Bert-VITS2-Korean, g2pK-based)
KR_REPO_DIR = Path(__file__).resolve().parent.parent / "_bert_vits2_kr"
KR_VENV_PY = KR_REPO_DIR / "venv" / "bin" / "python"
KR_RUNNER = KR_REPO_DIR / "run_infer_kr.py"
DEFAULT_KR_MODEL_DIR = KR_REPO_DIR / "models"
DEFAULT_KR_CONFIG = DEFAULT_KR_MODEL_DIR / "config.json"

DEFAULT_DEVICE = "cpu"  # safe default; MPS/CUDA opt-in via inputs


class BertVits2TTS(BaseTool):
    name = "bert_vits2_tts"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "tts"
    provider = "bert_vits2"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg", "python:g2pk"]
    install_instructions = (
        "Bert-VITS2 model not present. Setup:\n"
        "  python -m pip install g2pk jamo                 # Korean G2P (ko_g2p)\n"
        "  python tools/_bert_vits2/setup_bert_vits2.py   # multilingual v2.3 model\n"
        "  python tools/_bert_vits2_kr/setup_bert_vits2_kr.py  # Korean engine (train/import model)\n"
        "Multilingual needs the v2.3 weights (G_0.pth). The korean engine needs a\n"
        "trained Korean model (see skills/bert-vits2-tts.md)."
    )
    agent_skills = ["bert-vits2-tts"]

    capabilities = ["tts_zh", "tts_en", "tts_ja", "tts_ko_substitution", "tts_ko_native"]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to synthesize."},
            "engine": {
                "type": "string", "enum": ["multilingual", "korean"],
                "default": "multilingual",
                "description": "multilingual = fishaudio v2.3 (zh/en/ja + ko via ko_to_kana). korean = jwj7140/Bert-VITS2-Korean native KO (g2pK pronunciation).",
            },
            "language": {
                "type": "string", "enum": ["zh", "en", "ja", "ko"],
                "default": "ko",
                "description": "zh/en/ja for the multilingual engine. ko: multilingual→ja-substitution, korean engine→native g2pK.",
            },
            "speaker": {
                "type": "string",
                "description": "Speaker name from config.json spk2id, e.g. '派蒙_JP'. Defaults to the first speaker matching the language suffix.",
            },
            "length_scale": {"type": "number", "default": 1.0, "description": ">1 slower speech."},
            "sdp_ratio": {"type": "number", "default": 0.4},
            "noise_scale": {"type": "number", "default": 0.6},
            "noise_scale_w": {"type": "number", "default": 0.8},
            "device": {
                "type": "string", "enum": ["cpu", "mps", "cuda"], "default": "cpu",
                "description": "Inference device. cpu is the reliable default on Apple Silicon.",
            },
            "model_dir": {"type": "string", "description": "Override model directory."},
            "config": {"type": "string", "description": "Override config.json path."},
            "output_path": {"type": "string", "description": "Output WAV path."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=6144, vram_mb=0, disk_mb=3000)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["text", "language", "speaker", "length_scale"]
    side_effects = ["writes WAV to output_path", "loads local model (RAM-heavy)"]
    user_visible_verification = [
        "Listen for pronunciation quality; Korean is a Japanese-accented approximation",
        "Verify prosody matches the requested pacing (length_scale)",
    ]

    def get_status(self) -> ToolStatus:
        # any engine ready => usable; degraded if code ready but weights missing
        multi_ok = RUNNER.exists() and (DEFAULT_MODEL_DIR / "G_0.pth").exists()
        kr_ok = KR_RUNNER.exists() and (DEFAULT_KR_MODEL_DIR / "G_0.pth").exists()
        if multi_ok or kr_ok:
            return ToolStatus.AVAILABLE
        if RUNNER.exists() or KR_RUNNER.exists():
            return ToolStatus.DEGRADED  # code ready, model missing
        return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        if not (RUNNER.exists() or KR_RUNNER.exists()):
            raise DependencyError("Bert-VITS2 inference env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0  # local, free

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        # CPU inference is slow; model load dominates on first call.
        return 60.0

    def _resolve_speaker(self, hps_cfg: dict, language: str, explicit: str | None) -> str:
        if explicit:
            return explicit
        suffix = {"zh": "_ZH", "en": "_EN", "ja": "_JP", "ko": "_JP"}[language]
        for name in hps_cfg["data"]["spk2id"]:
            if name.endswith(suffix):
                return name
        return next(iter(hps_cfg["data"]["spk2id"]))

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text required")

        engine = inputs.get("engine", "multilingual")
        language = inputs.get("language", "ko")
        if language not in ("zh", "en", "ja", "ko"):
            return ToolResult(success=False, error=f"Unsupported language: {language}")
        if engine == "korean" and language != "ko":
            return ToolResult(success=False, error="korean engine only supports language='ko'")

        # ---- Korean-native engine (jwj7140, g2pK) --------------------------
        if engine == "korean":
            model_dir = Path(inputs.get("model_dir") or DEFAULT_KR_MODEL_DIR)
            config = Path(inputs.get("config") or model_dir / "config.json")
            if not (config.exists() and (model_dir / "G_0.pth").exists()):
                return ToolResult(
                    success=False,
                    error="Bert-VITS2-Korean model not present (needs training or a "
                    "downloaded G_0.pth + config.json under "
                    f"{DEFAULT_KR_MODEL_DIR}). See skills/bert-vits2-tts.md.",
                )
            if not (KR_VENV_PY.exists() and KR_RUNNER.exists()):
                return ToolResult(success=False, error="Korean engine venv missing. " + self.install_instructions)
            speaker = self._resolve_speaker(
                json.loads(config.read_text(encoding="utf-8")), "ko", inputs.get("speaker"))
            output = Path(inputs.get("output_path", "bert_vits2_ko.wav"))
            output.parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                str(KR_VENV_PY), str(KR_RUNNER),
                "--model-dir", str(model_dir), "--config", str(config),
                "--text", text, "--speaker", speaker, "--output", str(output),
                "--device", inputs.get("device", "cpu"),
                "--length-scale", str(inputs.get("length_scale", 1.0)),
                "--sdp-ratio", str(inputs.get("sdp_ratio", 0.4)),
                "--noise-scale", str(inputs.get("noise_scale", 0.6)),
                "--noise-scale-w", str(inputs.get("noise_scale_w", 0.8)),
            ]
            proc = self._run(cmd)
            if proc is None:
                return ToolResult(success=False, error="Bert-VITS2-Korean inference timed out")
            if proc.returncode != 0:
                return ToolResult(success=False, error="Bert-VITS2-Korean failed:\n" + (proc.stderr or proc.stdout)[-1200:])
            if not output.exists():
                return ToolResult(success=False, error="Korean inference produced no WAV")
            info = {"provider": self.provider, "engine": "korean", "language": "ko",
                    "speaker": speaker, "output": str(output)}
            try:
                info.update(json.loads(proc.stdout.strip().splitlines()[-1]))
            except Exception:
                pass
            return ToolResult(success=True, data=info, artifacts=[str(output)],
                              duration_seconds=round(time.time() - start, 2))

        # ---- Multilingual engine (fishaudio v2.3) --------------------------
        model_dir = Path(inputs.get("model_dir") or DEFAULT_MODEL_DIR)
        config = Path(inputs.get("config") or model_dir / "config.json")
        if not (config.exists() and (model_dir / "G_0.pth").exists()):
            return ToolResult(
                success=False,
                error="Bert-VITS2 multilingual model weights not downloaded yet. " + self.install_instructions,
            )

        # Korean → Japanese pronunciation substitution (multilingual engine only)
        bert_lang = {"ko": "JP", "ja": "JP", "en": "EN", "zh": "ZH"}[language]
        synth_text = hangul_to_hiragana(text) if language == "ko" else text

        speaker = self._resolve_speaker(json.loads(config.read_text(encoding="utf-8")), language, inputs.get("speaker"))

        output = Path(inputs.get("output_path", "bert_vits2_tts.wav"))
        output.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(VENV_PY), str(RUNNER),
            "--model-dir", str(model_dir),
            "--config", str(config),
            "--text", synth_text,
            "--language", bert_lang,
            "--speaker", speaker,
            "--output", str(output),
            "--device", inputs.get("device", "cpu"),
            "--length-scale", str(inputs.get("length_scale", 1.0)),
            "--sdp-ratio", str(inputs.get("sdp_ratio", 0.4)),
            "--noise-scale", str(inputs.get("noise_scale", 0.6)),
            "--noise-scale-w", str(inputs.get("noise_scale_w", 0.8)),
        ]

        proc = self._run(cmd)
        if proc is None:
            return ToolResult(success=False, error="Bert-VITS2 inference timed out after 30min")
        if proc.returncode != 0:
            return ToolResult(
                success=False,
                error="Bert-VITS2 inference failed:\n" + (proc.stderr or proc.stdout)[-1200:],
                data={"full_stderr": proc.stderr, "full_stdout": proc.stdout},
            )
        if not output.exists():
            return ToolResult(success=False, error="Inference succeeded but no output WAV")

        info = {"provider": self.provider, "language": language,
                "synthesized_as": bert_lang, "speaker": speaker, "output": str(output)}
        try:
            meta = json.loads(proc.stdout.strip().splitlines()[-1])
            info.update(meta)
        except Exception:
            pass
        return ToolResult(success=True, data=info, artifacts=[str(output)],
                          duration_seconds=round(time.time() - start, 2))

    @staticmethod
    def _run(cmd: list[str]):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=1800)
        except subprocess.TimeoutExpired:
            return None
