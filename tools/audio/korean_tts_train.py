"""Korean Bert-VITS2 training tool for OpenMontage.

Orchestrates the full Korean data pipeline: raw audio + transcript ->
44.1kHz resample -> g2pK-preprocessed filelists -> KO-only config ->
spec + KoBERT features -> train_ms.py -> a G_*.pth model consumable by
`bert_vits2_tts` (engine="korean").

The heavy compute (spec_gen / bert_gen / train_ms) requires CUDA in practice;
on CPU/MPS the pipeline runs but training is impractically slow.

Run the one-time engine setup first:
  python tools/_bert_vits2_kr/setup_bert_vits2_kr.py
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

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

KR_REPO_DIR = Path(__file__).resolve().parent.parent / "_bert_vits2_kr"
KR_VENV_PY = KR_REPO_DIR / "venv" / "bin" / "python"
PIPELINE = KR_REPO_DIR / "train_korean.py"


class KoreanTTSTrain(BaseTool):
    name = "korean_tts_train"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "training"
    provider = "bert_vits2"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = (
        "Korean-engine venv missing. Run:\n"
        "  python tools/_bert_vits2_kr/setup_bert_vits2_kr.py\n"
        "Requires CUDA GPU for practical training."
    )
    agent_skills = ["bert-vits2-tts"]

    capabilities = ["train_korean_model", "preprocess_korean", "generate_ko_config"]

    input_schema = {
        "type": "object",
        "required": ["audios_dir", "transcript"],
        "properties": {
            "audios_dir": {"type": "string", "description": "Raw Korean audio directory (wav/mp3/flac/m4a)."},
            "transcript": {"type": "string", "description": "KSS-style transcript file: '<name> <korean text>' per line."},
            "speaker_name": {"type": "string", "default": "speaker1"},
            "work_dir": {"type": "string", "description": "Pipeline working dir (default tools/_bert_vits2_kr/Data/<name>)."},
            "device": {"type": "string", "enum": ["cuda", "mps", "cpu"], "default": "cuda"},
            "epochs": {"type": "integer", "default": 500},
            "batch_size": {"type": "integer", "default": 16},
            "num_workers": {"type": "integer", "default": 8},
            "dry_run": {"type": "boolean", "default": False, "description": "Print pipeline commands without running."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=8, ram_mb=16384, vram_mb=8192, disk_mb=20000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["audios_dir", "transcript", "speaker_name"]
    side_effects = ["trains a model (hours on GPU)", "writes datasets + checkpoints under work_dir"]
    user_visible_verification = [
        "Audition the trained model with bert_vits2_tts(engine='korean')",
        "Confirm pronunciation follows g2pK (script text -> spoken form)",
    ]

    def get_status(self) -> ToolStatus:
        if not (KR_VENV_PY.exists() and PIPELINE.exists()):
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (KR_VENV_PY.exists() and PIPELINE.exists()):
            raise DependencyError("Korean training env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        # realistic: hours on GPU for a few hundred epochs
        return 4 * 3600.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        audios = Path(inputs.get("audios_dir", ""))
        transcript = Path(inputs.get("transcript", ""))
        if not audios.is_dir() or not transcript.is_file():
            return ToolResult(success=False, error="audios_dir (dir) and transcript (file) required")

        speaker = inputs.get("speaker_name", "speaker1")
        work = inputs.get("work_dir") or str(KR_REPO_DIR / "Data" / speaker)
        cmd = [
            str(KR_VENV_PY), str(PIPELINE),
            "--audios-dir", str(audios),
            "--transcript", str(transcript),
            "--speaker-name", speaker,
            "--work-dir", work,
            "--device", inputs.get("device", "cuda"),
            "--epochs", str(inputs.get("epochs", 500)),
            "--batch-size", str(inputs.get("batch_size", 16)),
            "--num-workers", str(inputs.get("num_workers", 8)),
        ]
        if inputs.get("dry_run"):
            cmd.append("--dry-run")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=6 * 3600)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Training timed out after 6h")

        if proc.returncode != 0:
            return ToolResult(
                success=False,
                error="Korean training pipeline failed:\n" + (proc.stderr or proc.stdout)[-1500:],
                data={"full_stderr": proc.stderr},
            )

        models_dir = Path(work) / "models"
        ckpts = sorted(models_dir.glob("G_*.pth")) if models_dir.exists() else []
        return ToolResult(
            success=True,
            data={
                "provider": self.provider, "work_dir": work,
                "model_checkpoints": [str(c) for c in ckpts],
                "config": str(Path(work) / "config.json"),
                "dry_run": bool(inputs.get("dry_run")),
            },
            duration_seconds=round(time.time() - start, 2),
        )
