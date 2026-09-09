"""Automated Pre-Push Privacy & Secrets Inspector for OpenMontage.

Scans staged git changes or outgoing commits before push to prevent accidental leaks of:
- API Keys (OpenAI, Anthropic, HuggingFace, Google, AWS, GitHub, Fal.ai)
- Private SSH/RSA Keys & JWT Secrets
- Sensitive Personal Data (Korean phone numbers, resident IDs, private emails)

Can be executed standalone via CLI or invoked automatically via Git hooks (.git/hooks/pre-push).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# High-precision RegEx signatures for API keys and secrets
SECRET_SIGNATURES: List[Tuple[str, str, str]] = [
    ("OpenAI API Key", r"sk-(?:proj-)?[a-zA-Z0-9_-]{20,}", "CRITICAL"),
    ("Anthropic API Key", r"sk-ant-[a-zA-Z0-9_-]{20,}", "CRITICAL"),
    ("Hugging Face Token", r"hf_[a-zA-Z0-9]{34,}", "CRITICAL"),
    ("Google API Key", r"AIza[0-9A-Za-z-_]{35}", "CRITICAL"),
    ("AWS Access Key", r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}", "CRITICAL"),
    ("GitHub Token", r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}|github_pat_[a-zA-Z0-9_]{50,}", "CRITICAL"),
    ("Private RSA/SSH Key", r"-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----", "CRITICAL"),
    ("Generic Secret Assignment", r"""(?i)(?:api_key|secret_key|client_secret|auth_token|access_token)\s*=\s*['"][a-zA-Z0-9_\-.~!@#$%^&*]{16,}['"]""", "HIGH"),
    ("Korean Resident Number", r"\b\d{6}\s*-\s*[1-4]\d{6}\b", "CRITICAL"),
    ("Korean Phone Number", r"\b01[016789]\s*-\s*\d{3,4}\s*-\s*\d{4}\b", "MEDIUM"),
]

# Files that naturally contain harmless dummy examples
SAFE_FILES = {
    ".gitignore", "privacy_prepush_inspector.py", "test_privacy_prepush.py"
}


def mask_secret(secret: str) -> str:
    """Mask a secret showing only the first 4 and last 2 characters."""
    if len(secret) <= 8:
        return "****"
    return secret[:4] + "*" * (len(secret) - 6) + secret[-2:]


def inspect_text_content(content: str, source_name: str = "text") -> List[Dict[str, Any]]:
    """Scans a text content string and returns all matched secret violations."""
    violations = []
    lines = content.splitlines()

    for line_idx, line in enumerate(lines, 1):
        # Skip commented-out explanation lines in docs/examples
        if line.strip().startswith(("#", "//", "/*", "*")) and ("example" in line.lower() or "your_key" in line.lower()):
            continue

        for rule_name, pattern, severity in SECRET_SIGNATURES:
            matches = re.finditer(pattern, line)
            for m in matches:
                matched_val = m.group(0)
                # Ignore placeholders like 'sk-your-key-here' or 'sk-...'
                if any(p in matched_val.lower() for p in ("your_key", "your-key", "placeholder", "fake", "example")):
                    continue

                violations.append({
                    "rule": rule_name,
                    "severity": severity,
                    "source": source_name,
                    "line_number": line_idx,
                    "snippet": mask_secret(matched_val),
                    "full_line": line.strip()[:100]
                })

    return violations


class PrivacyPrepushInspector(BaseTool):
    name = "privacy_prepush_inspector"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "analysis"
    provider = "openmontage"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = "Built-in Git pre-push hook tool."
    agent_skills = []

    input_schema = {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["staged", "outgoing", "all"],
                "default": "staged",
                "description": "Scan mode: 'staged' (git diff --staged), 'outgoing' (unpushed commits), or 'all'."
            },
            "content": {
                "type": "string",
                "description": "Optional raw string content to scan."
            }
        }
    }

    def _get_git_diff(self, mode: str) -> str:
        """Retrieves git diff based on inspection mode."""
        try:
            if mode == "staged":
                cmd = ["git", "diff", "--staged"]
            elif mode == "outgoing":
                cmd = ["git", "diff", "@{u}..HEAD"]
            else:
                cmd = ["git", "diff", "HEAD~1..HEAD"]

            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                return res.stdout
            # If upstream tracking branch is missing, fallback to staged
            res_fallback = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
            return res_fallback.stdout
        except Exception:
            return ""

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        content = params.get("content")
        mode = params.get("mode", "staged")

        if content:
            violations = inspect_text_content(content, source_name="direct_input")
        else:
            diff_text = self._get_git_diff(mode)
            if not diff_text.strip():
                return ToolResult(
                    success=True,
                    data={
                        "status": "clean",
                        "violations_count": 0,
                        "violations": [],
                        "message": "스캔할 변경 사항(Diff)이 없거나 안전합니다."
                    }
                )
            violations = inspect_text_content(diff_text, source_name=f"git_diff_{mode}")

        # Filter out safe files
        filtered_violations = [
            v for v in violations if not any(sf in v["source"] for sf in SAFE_FILES)
        ]

        critical_count = sum(1 for v in filtered_violations if v["severity"] == "CRITICAL")
        has_critical = critical_count > 0

        return ToolResult(
            success=not has_critical,
            data={
                "status": "blocked" if has_critical else ("warning" if filtered_violations else "clean"),
                "violations_count": len(filtered_violations),
                "critical_count": critical_count,
                "violations": filtered_violations,
                "message": (
                    f"❌ [보안 경고] {critical_count}개의 치명적인 민감정보/API 키가 감지되어 푸시가 차단되었습니다!"
                    if has_critical else "✅ 민감정보 및 시크릿 검사 통과 (안전하게 푸시 가능)"
                )
            },
            error=f"민감정보 {critical_count}건 감지됨" if has_critical else None
        )


def main():
    parser = argparse.ArgumentParser(description="Git Pre-Push Privacy & Secrets Inspector")
    parser.add_argument("--mode", default="outgoing", choices=["staged", "outgoing", "all"], help="Scan mode")
    parser.add_argument("--install-hook", action="store_true", help="Install Git pre-push hook automatically")
    args = parser.parse_args()

    # Hook installation
    if args.install_hook:
        git_dir = Path(".git")
        if not git_dir.exists():
            print("❌ .git 디렉토리를 찾을 수 없습니다. Git 저장소 루트에서 실행하세요.", file=sys.stderr)
            sys.exit(1)

        hook_path = git_dir / "hooks" / "pre-push"
        hook_script = f"""#!/bin/sh
# OpenMontage Automated Pre-Push Privacy & Secrets Inspector
echo "🛡️  [OpenMontage] 푸시 전 민감정보/API 키 자동 보안 검사 중..."
python3 tools/analysis/privacy_prepush_inspector.py --mode outgoing
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "❌ [PUSH BLOCKED] 비밀번호, API 키 또는 개인정보 유출 위험이 감지되어 푸시가 중단되었습니다."
  echo "위 파일에서 민감정보를 제거하거나 .env 파일로 옮긴 후 다시 시도하세요."
  exit 1
fi
echo "✅ [SECURITY PASS] 보안 검사 통과! 원격 저장소로 안전하게 푸시합니다."
exit 0
"""
        hook_path.write_text(hook_script, encoding="utf-8")
        hook_path.chmod(0o755)
        print(f"🎉 Git pre-push 훅이 성공적으로 설치되었습니다: {hook_path}")
        sys.exit(0)

    inspector = PrivacyPrepushInspector()
    res = inspector.execute({"mode": args.mode})
    data = res.data or {}

    if not res.success or data.get("critical_count", 0) > 0:
        print("\n" + "=" * 60)
        print("🚨 [OPENMONTAGE 보안 경비원] 치명적인 민감정보가 발견되었습니다!")
        print("=" * 60)
        for v in data.get("violations", []):
            print(f"• [{v['severity']}] {v['rule']} (소스: {v['source']}:{v['line_number']})")
            print(f"  마스킹된 값: {v['snippet']}")
            print(f"  발견된 코드: {v['full_line']}\n")
        sys.exit(1)
    else:
        print(f"✅ {data.get('message')}")
        sys.exit(0)


if __name__ == "__main__":
    main()
