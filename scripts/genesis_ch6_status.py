#!/usr/bin/env python3
"""genesis_ch6_status.py — Real-time progress monitor for Genesis Ch 6-50 (100 Shorts)."""
import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "projects" / "_genesis_from_ch6_series" / "genesis_ch6_100_manifest.json"

if not MANIFEST_PATH.exists():
    print("Manifest not found. Run scripts/build_ch6_manifest.py first.")
    exit(1)

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

episodes = manifest.get("episodes", [])
completed = [ep for ep in episodes if ep.get("status") == "completed"]
total = len(episodes)
pct = (len(completed) / total) * 100

print("=" * 68)
print(f"🏆 {manifest.get('series_title', 'Genesis Ch 6-50 (100 Shorts)')}")
print(f"📊 총 진행률: {len(completed)} / {total} 편 완료 ({pct:.1f}%) · 소요 비용: 0 크레딧 ($0.00)")
print("=" * 68)

print("\n[✅ 완료된 에피소드]")
for ep in completed:
    r_path = ep.get("render_path", "")
    p = Path(__file__).resolve().parent.parent / r_path if r_path else None
    size_str = f"({p.stat().st_size / (1024*1024):.1f} MB)" if p and p.exists() else ""
    print(f"  • [Ep {ep['episode_number']:03d}] {ep['title']} {size_str}")
    if r_path:
        print(f"    └── 파일: {r_path}")

pending = [ep for ep in episodes if ep.get("status") != "completed"]
print(f"\n[⏳ 대기 중인 에피소드 ({len(pending)}편)]")
for ep in pending[:6]:
    print(f"  • [Ep {ep['episode_number']:03d}] {ep['title']}")
if len(pending) > 6:
    print(f"  ... 외 {len(pending) - 6}편 대기 중")

print("\n" + "=" * 68)
print("💡 실행 명령어 안내:")
print("  - 특정 에피소드 1편 제작 : python scripts/batch_genesis_ch6_factory.py --episode <번호>")
print("  - 범위 지정 일괄 제작   : python scripts/batch_genesis_ch6_factory.py --start 2 --end 10")
print("  - 전체 100편 순차 가동  : nohup python -u scripts/batch_genesis_ch6_factory.py --start 2 --end 100 > genesis_ch6_batch.log 2>&1 &")
print("=" * 68)
