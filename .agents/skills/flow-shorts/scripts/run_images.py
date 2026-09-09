#!/usr/bin/env python3
"""flow-shorts stage 1 — generate images (0 credits) via Google Flow.

Reads flow.json, drives the Flow UI over CDP:
  1. Build the ANCHOR image first (no reference).
  2. Every other image is generated with the anchor attached as a reference
     image, so the whole set shares one look.
  3. State (image_id -> Flow card title, prompt, status) is appended to
     <output>/state.json after every image -> resumable.

Usage:
  python3 run_images.py --config flow.json --output ./flow_assets \
      [--limit 1] [--only IMAGE_ID] [--chrome-port 9222]
"""
from __future__ import annotations

import argparse
import json
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
    return {"images": {}}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--limit", type=int, default=0,
                    help="generate at most N images (use --limit 1 for the anchor-only test run)")
    ap.add_argument("--only", help="generate only this image id")
    ap.add_argument("--chrome-port", type=int, default=9222)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    screenshots = out_dir / "screenshots"
    state_path = out_dir / "state.json"
    state = load_state(state_path)

    images = cfg["images"]
    look = cfg.get("look_prompt", "")
    aspect = cfg.get("aspect_ratio", "9:16")
    anchors = [img for img in images if img.get("anchor")]
    if len(anchors) != 1:
        fail("flow.json images[] must contain exactly ONE anchor:true entry")
    anchor = anchors[0]
    others = [img for img in images if not img.get("anchor")]

    queue: list[dict] = [anchor] + others
    if args.only:
        queue = [img for img in images if img["id"] == args.only]
        if not queue:
            fail(f"no image with id {args.only}")
    if args.limit:
        queue = queue[: args.limit]

    # already-done items are skipped (resume support)
    queue = [img for img in queue
             if not (state["images"].get(img["id"], {}).get("status") == "done")]
    if not queue:
        print(json.dumps({"ok": True, "done": True, "message": "all images already done"}, ensure_ascii=False))
        return

    ws_url = get_ws_url(args.chrome_port, cfg.get("flow_url", "https://labs.google/fx/ko/tools/flow"))
    harness = FlowHarness(ws_url, screenshots)
    try:
        selectors = harness.selectors

        for img in queue:
            img_id = img["id"]
            prompt = look + " " + img["prompt"] if look else img["prompt"]
            is_anchor = bool(img.get("anchor"))

            # 1. focus the prompt box and type
            box_spec = selectors["prompt_box"]
            before_titles = harness.get_card_titles()
            try:
                node = harness.node_from_ref(box_spec)
                harness.type_into_node(node, prompt)
            except LookupError as e:
                shot = harness.screenshot(f"fail_prompt_{img_id}")
                fail(f"prompt box not found for {img_id}: {e}", shot)

            # 2. attach anchor as reference (non-anchor images only)
            if not is_anchor:
                anchor_state = state["images"].get(anchor["id"], {})
                anchor_file = out_dir / "images" / f"{anchor['id']}.png"
                if anchor_state.get("status") != "done" or not anchor_file.exists():
                    fail(f"anchor {anchor['id']} must be generated (and downloaded) before {img_id}")
                try:
                    ref_btn = harness.node_from_ref(selectors["add_reference_button"])
                    harness.click_node(ref_btn)
                    harness.wait(1.0)
                    file_input = harness.node_from_ref(selectors["reference_file_input"])
                    harness.set_file_input(file_input, anchor_file)
                    harness.wait(1.0)
                except LookupError as e:
                    shot = harness.screenshot(f"fail_ref_{img_id}")
                    fail(f"reference attach failed for {img_id}: {e}", shot)

            # 3. press create
            try:
                btn = harness.node_from_ref(selectors["create_button"])
                harness.click_node(btn)
            except LookupError as e:
                shot = harness.screenshot(f"fail_create_{img_id}")
                fail(f"create button not found for {img_id}: {e}", shot)

            # 4. wait for a NEW card title to appear (most stable completion signal)
            new_title = harness.wait_for_new_card_title(before_titles, timeout=240)
            if new_title is None:
                shot = harness.screenshot(f"fail_timeout_{img_id}")
                state["images"][img_id] = {"status": "timeout", "prompt": prompt}
                save_state(state_path, state)
                fail(f"timed out waiting for new card (image {img_id})", shot)

            harness.wait(harness.SETTLE_DELAY)
            # 5. download the asset
            url = harness.get_asset_url(new_title)
            img_dir = out_dir / "images"
            img_dir.mkdir(exist_ok=True)
            dest = img_dir / f"{img_id}.png"
            if url:
                harness.download_asset(url, dest)
            state["images"][img_id] = {
                "status": "done", "prompt": prompt, "flow_title": new_title,
                "url": url, "file": str(dest),
            }
            save_state(state_path, state)
            print(json.dumps({"ok": True, "image": img_id, "flow_title": new_title,
                              "file": str(dest)}, ensure_ascii=False), flush=True)
            harness.wait(2.0)

        print(json.dumps({"ok": True, "done": True, "generated": len(queue)}, ensure_ascii=False))
    finally:
        harness.close()


if __name__ == "__main__":
    main()