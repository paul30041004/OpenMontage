#!/usr/bin/env python3
"""flow-shorts stage 2 — convert selected images to video clips (spends credits).

Reads flow.json clips[] where each clip names its source image by ID.
The source image is located in the Flow asset list BY CARD TITLE (recorded in
state.json during stage 1), never by list position — selection reorders the
list, so positional picking reliably burns credits on the wrong asset.

Safety gates before any credit is spent:
  1. clip prompt must be one slow camera move (warn if longer than ~120 chars)
  2. output count shown in the UI must be 1 (fresh accounts default to 2)
     -> abort if it is not 1, BEFORE clicking create
  3. anchor-style state recording + failure screenshots

Usage:
  python3 run_clips.py --config flow.json --output ./flow_assets \
      [--only CLIP_ID] [--chrome-port 9222]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from browser_harness import FlowHarness, get_ws_url


def fail(msg: str, screenshot: Path | None = None) -> None:
    print(json.dumps({"ok": False, "error": msg,
                      "screenshot": str(screenshot) if screenshot else None},
                     ensure_ascii=False))
    sys.exit(1)


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"images": {}, "clips": {}}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--only")
    ap.add_argument("--chrome-port", type=int, default=9222)
    ap.add_argument("--force", action="store_true",
                    help="skip the credit pre-flight check (NOT recommended)")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.output)
    screenshots = out_dir / "screenshots"
    state_path = out_dir / "state.json"
    state = load_state(state_path)

    clips = cfg["clips"]
    if args.only:
        clips = [c for c in clips if c["id"] == args.only]
        if not clips:
            fail(f"no clip with id {args.only}")

    clips = [c for c in clips
             if not (state.get("clips", {}).get(c["id"], {}).get("status") == "done")]
    if not clips:
        print(json.dumps({"ok": True, "done": True, "message": "all clips already done"}, ensure_ascii=False))
        return

    # pre-flight: every clip's source image must exist in state
    for c in clips:
        src = state["images"].get(c["source_image"])
        if not src or src.get("status") != "done" or not src.get("flow_title"):
            fail(f"source image {c['source_image']} not generated yet (run run_images.py first)")

    ws_url = get_ws_url(args.chrome_port, cfg.get("flow_url", "https://labs.google/fx/ko/tools/flow"))
    harness = FlowHarness(ws_url, screenshots)
    try:
        selectors = harness.selectors
        state.setdefault("clips", {})

        for clip in clips:
            clip_id = clip["id"]
            prompt = clip.get("prompt",
                              "첫 프레임 그대로 유지하고 아주 느린 카메라 이동")

            # soft guard: clip prompts should stay minimal
            if len(prompt) > 120:
                print(json.dumps({"warn": f"clip {clip_id} prompt is long ({len(prompt)} chars); "
                                          "rich prompts make the frame drift"}, ensure_ascii=False))

            before_titles = harness.get_card_titles()
            source_title = state["images"][clip["source_image"]]["flow_title"]

            # 1. open image-to-video on the SOURCE CARD (by title, not position)
            found = harness.eval_js(
                "(() => { const cards = Array.from(document.querySelectorAll("
                "'[data-testid*=\"asset\"], [class*=\"card\"]'));"
                "const card = cards.find(c => (c.innerText || '').includes("
                + json.dumps(source_title) + "));"
                "if (!card) return 'card-not-found';"
                "const btn = Array.from(card.querySelectorAll('button')).find("
                "b => /영상|비디오|클립|video/i.test(b.textContent + ' ' + (b.getAttribute('aria-label')||'')));"
                "if (!btn) return 'btn-not-found';"
                "btn.scrollIntoView({block:'center'}); btn.click(); return 'ok'; })()"
            )
            if found != "ok":
                shot = harness.screenshot(f"fail_open_{clip_id}")
                fail(f"could not open image-to-video on card '{source_title}' ({found})", shot)
            harness.wait(2.0)

            # 2. type the clip prompt
            try:
                node = harness.node_from_ref(selectors["clip_prompt_box"])
                harness.type_into_node(node, prompt)
            except LookupError as e:
                shot = harness.screenshot(f"fail_prompt_{clip_id}")
                fail(f"clip prompt box not found for {clip_id}: {e}", shot)

            # 3. credit gate: output count must read 1 — check BEFORE creating
            count = harness.eval_js(selectors["clip_output_count"]["js"])
            if count != "1" and not args.force:
                shot = harness.screenshot(f"fail_count_{clip_id}")
                fail(f"output count is {count!r}, expected '1' — fix the count setting "
                     f"in the UI before spending credits (use --force to override)", shot)

            # 4. create the clip
            try:
                btn = harness.node_from_ref(selectors["create_clip_button"])
                harness.click_node(btn)
            except LookupError as e:
                shot = harness.screenshot(f"fail_create_{clip_id}")
                fail(f"create button not found for {clip_id}: {e}", shot)

            # 5. wait for the new clip card (title-based completion signal)
            new_title = harness.wait_for_new_card_title(before_titles, timeout=420)
            if new_title is None:
                shot = harness.screenshot(f"fail_timeout_{clip_id}")
                state["clips"][clip_id] = {"status": "timeout", "prompt": prompt}
                save_state(state_path, state)
                fail(f"timed out waiting for clip card (clip {clip_id})", shot)

            harness.wait(harness.SETTLE_DELAY)
            url = harness.get_asset_url(new_title)
            clip_dir = out_dir / "clips"
            clip_dir.mkdir(exist_ok=True)
            dest = clip_dir / f"{clip_id}.mp4"
            if url:
                harness.download_asset(url, dest)
            state["clips"][clip_id] = {
                "status": "done", "prompt": prompt, "source_image": clip["source_image"],
                "flow_title": new_title, "url": url, "file": str(dest),
            }
            save_state(state_path, state)
            print(json.dumps({"ok": True, "clip": clip_id, "flow_title": new_title,
                              "file": str(dest)}, ensure_ascii=False), flush=True)
            harness.wait(2.0)

        print(json.dumps({"ok": True, "done": True, "generated": len(clips)}, ensure_ascii=False))
    finally:
        harness.close()


if __name__ == "__main__":
    main()