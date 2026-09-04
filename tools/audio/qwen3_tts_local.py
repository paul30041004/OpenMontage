"""Qwen3-TTS local TTS tool — official qwen-tts package on Apple Silicon (MPS).

Runs the official Qwen3-TTS models via the `qwen-tts` pip package (transformers
backed) with locally downloaded weights:

- CustomVoice 1.7B  — 9 premium speakers incl. Korean 'Sohee' (style control via instruct)
- Base 1.7B         — 3-second zero-shot voice cloning from a reference audio clip

Unlike `qwen3_tts` (mlx-audio port), this tool uses the official implementation
and local model directories, so Korean voice cloning works reliably.

Usage:
    t = Qwen3TTSLocal()
    t.execute({
        "mode": "clone",
        "text": "안녕하세요.",
        "reference_audio": "voice_library/comfort_heal.wav",
        "reference_text": "힘들면 잠시 쉬어도 괜찮아요.",
        "output_path": "output.wav",
    })
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

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

PYTHON_BIN = "/Users/paul/qwen-tts-venv/bin/python"
MODELS_DIR = Path("/Users/paul/qwen-tts-models")

_MODEL_DIRS = {
    "custom_1.7b": MODELS_DIR / "Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "base_1.7b": MODELS_DIR / "Qwen3-TTS-12Hz-1.7B-Base",
}

# Reference audio search roots (checked in order; first hit wins)
REF_SEARCH_ROOTS = [
    Path("voice_library"),
    Path("voice_samples"),
    Path("assets"),
    Path("test_audio"),
]

# Common audio extensions used when scanning reference folders
_REF_EXTS = (".wav", ".mp3", ".flac", ".m4a", ".ogg")

_SPEAKERS = ["Vivian", "Serena", "Uncle_Fu", "Dylan", "Eric", "Ryan", "Aiden", "Ono_Anna", "Sohee"]
_LANGS = ["Auto", "Chinese", "English", "Japanese", "Korean", "German", "French", "Russian", "Portuguese", "Spanish", "Italian"]


def discover_reference_audio(root: str | Path | None = None) -> list[dict[str, Any]]:
    """Scan reference audio folders and return a list of {path, name, duration_seconds}."""
    roots = []
    if root:
        roots = [Path(root)]
    else:
        roots = [Path(p) for p in REF_SEARCH_ROOTS if Path(p).exists()]
    found: list[dict[str, Any]] = []
    for r in roots:
        if not r.exists():
            continue
        for p in sorted(r.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in _REF_EXTS:
                continue
            dur: float | None = None
            try:
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                    capture_output=True, text=True, timeout=15,
                )
                if probe.returncode == 0 and probe.stdout.strip():
                    dur = round(float(probe.stdout.strip()), 2)
            except Exception:
                dur = None
            found.append({"path": str(p), "name": p.name, "duration_seconds": dur})
    return found


class Qwen3TTSLocal(BaseTool):
    name = "qwen3_tts_local"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "qwen3_local"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL_GPU

    dependencies = [f"path:{PYTHON_BIN}"]
    install_instructions = (
        "Requires Python venv at /Users/paul/qwen-tts-venv with `pip install -U qwen-tts`, "
        "and model weights under /Users/paul/qwen-tts-models/ (Qwen3-TTS-12Hz-1.7B-CustomVoice + "
        "-Base + Qwen3-TTS-Tokenizer-12Hz). Uses Apple Silicon MPS."
    )
    fallback = "qwen3_tts"
    fallback_tools = ["qwen3_tts", "fish_audio_local_tts", "voxcpm_tts"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "custom_voice",
        "multilingual",
        "local_tts",
    ]
    supports = {
        "voice_cloning": True,
        "custom_voice": True,
        "multilingual": True,
        "offline": True,
        "apple_silicon_mps": True,
        "korean": True,
    }
    best_for = [
        "3-second zero-shot voice cloning in Korean (official qwen-tts)",
        "9 premium speakers incl. 'Sohee' Korean female (CustomVoice)",
        "fully offline local TTS on Apple Silicon",
    ]
    not_good_for = [
        "SSML markup control",
        "voice design from natural-language persona (use Qwen3-TTS VoiceDesign or qwen3_tts design_1.7b)",
    ]

    input_schema = {
        "type": "object",
        "required": ["text", "mode"],
        "properties": {
            "text": {"type": "string", "description": "Text to synthesize."},
            "mode": {
                "type": "string",
                "enum": ["clone", "custom_voice", "discover_references"],
                "description": "clone=zero-shot clone from reference audio (Base model); custom_voice=premium speaker (CustomVoice model); discover_references=scan folders and return the reference audio list.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to reference audio for voice cloning. Accepts a full path or a bare filename matched against voice_library/, voice_samples/, assets/, test_audio/.",
            },
            "reference_text": {
                "type": "string",
                "description": "Transcript of the reference clip (improves clone fidelity). Optional but recommended.",
            },
            "speaker": {
                "type": "string",
                "enum": _SPEAKERS,
                "default": "Sohee",
                "description": "Premium speaker for mode=custom_voice.",
            },
            "instruct": {
                "type": "string",
                "description": "Optional style instruction (tone/emotion/prosody) for CustomVoice. Omit for natural reading.",
            },
            "language": {
                "type": "string",
                "enum": _LANGS,
                "default": "Korean",
                "description": "Spoken-language hint. 'Auto' lets the model detect from text.",
            },
            "max_new_tokens": {
                "type": "integer",
                "default": 2048,
                "description": "Generation token cap for a long sentence or batch.",
            },
            "output_path": {
                "type": "string",
                "description": "Output WAV path (default: qwen3_tts_local.wav).",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=10240, vram_mb=8192, disk_mb=500, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])

    def get_status(self) -> ToolStatus:
        if PYTHON_BIN and Path(PYTHON_BIN).exists():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return max(10.0, len(inputs.get("text", "")) * 0.25)

    def _resolve_ref(self, ref: str) -> Path | None:
        p = Path(ref)
        if p.is_file():
            return p
        for root in REF_SEARCH_ROOTS:
            if not root.exists():
                continue
            cand = root / ref
            if cand.is_file():
                return cand
            hits = [f for f in root.rglob("*") if f.is_file() and f.name == ref]
            if hits:
                return hits[0]
        return None

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        mode = inputs.get("mode", "")

        # --- reference audio discovery (no model load) ---
        if mode == "discover_references":
            root = inputs.get("reference_audio") or None  # optional custom root
            found = discover_reference_audio(root)
            return ToolResult(
                success=True,
                data={
                    "mode": "discover_references",
                    "count": len(found),
                    "references": found,
                    "search_roots": [str(r) for r in REF_SEARCH_ROOTS] if not root else [root],
                },
            )

        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text is required")

        if mode == "clone":
            ref = inputs.get("reference_audio")
            if not ref:
                return ToolResult(
                    success=False,
                    error="mode=clone requires reference_audio — run mode=discover_references to list available clips",
                )
            ref_path = self._resolve_ref(ref)
            if not ref_path:
                return ToolResult(
                    success=False,
                    error=f"reference_audio not found: {ref}. Use mode=discover_references to list candidates.",
                )
            model_dir = _MODEL_DIRS["base_1.7b"]
            gen_fn = "generate_voice_clone"
            gen_kw = [
                f"ref_audio={json.dumps(str(ref_path))}",
                f"ref_text={json.dumps(inputs.get('reference_text') or '')}",
            ]
        elif mode == "custom_voice":
            model_dir = _MODEL_DIRS["custom_1.7b"]
            gen_fn = "generate_custom_voice"
            gen_kw = [f"speaker={json.dumps(inputs.get('speaker', 'Sohee'))}"]
            instruct = inputs.get("instruct")
            if instruct:
                gen_kw.append(f"instruct={json.dumps(instruct)}")
        else:
            return ToolResult(
                success=False,
                error=f"unknown mode '{mode}' (use 'clone', 'custom_voice', or 'discover_references')",
            )

        if not model_dir.exists():
            return ToolResult(
                success=False,
                error=f"model weights missing at {model_dir} — download via huggingface-cli first",
            )

        output_path = Path(inputs.get("output_path", "qwen3_tts_local.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        gen_kw_str = ", ".join(gen_kw)
        lang = inputs.get("language", "Korean")
        max_tokens = int(inputs.get("max_new_tokens", 2048))

        script = f"""
import torch, soundfile as sf, json
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    {json.dumps(str(model_dir))},
    dtype=torch.bfloat16,
    device_map="mps",
)
wavs, sr = model.{gen_fn}(
    text={json.dumps(text)},
    language={json.dumps(lang)},
    {gen_kw_str},
    max_new_tokens={max_tokens},
)
sf.write({json.dumps(str(output_path))}, wavs[0], sr)
print("DONE", sr)
"""
        start = time.time()
        try:
            res = subprocess.run(
                [PYTHON_BIN, "-c", script],
                capture_output=True,
                text=True,
                check=True,
                timeout=900,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Qwen3-TTS (local) generation failed: {exc}",
            )

        if not output_path.exists() or output_path.stat().st_size < 1000:
            stderr = res.stderr[-800:] if res.stderr else ""
            return ToolResult(
                success=False,
                error=f"Output audio not created. stderr: {stderr}",
            )

        dur = None
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(output_path)],
                capture_output=True, text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = round(float(probe.stdout.strip()), 2)
        except Exception:
            dur = None

        elapsed = round(time.time() - start, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "qwen3_local",
                "tool": "qwen3_tts_local",
                "mode": mode,
                "model": str(model_dir.name),
                "output": str(output_path),
                "duration_seconds": dur,
                "generation_seconds": elapsed,
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
        )
