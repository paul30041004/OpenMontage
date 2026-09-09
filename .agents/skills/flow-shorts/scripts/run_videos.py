#!/usr/bin/env python3
"""flow-shorts stage 2b — generate VIDEOS at ZERO credits.

Uses the "Veo 3.1 - Lite [Lower Priority]" model in Google Flow, which is
verified to generate 720p 9:16 videos for 0 credits ("Generating will use
0 credits" shown in the settings panel). Lower-priority means requests are
queued behind paid ones — generation takes ~3-10 minutes per clip and can
stall for long stretches at a fixed percentage. That is normal; keep waiting.

Because generation is free, this script defaults to the x4 batch option —
one prompt yields FOUR variants; the best one gets picked manually and the
rest discarded. All four are downloaded so the choice happens offline.

Safety gates:
  1. The settings panel MUST show "use 0 credits" before the create button
     is pressed. If it shows any non-zero credit cost (model renamed/removed
     by Google), the script aborts BEFORE spending anything.
  2. Every failure saves a screenshot to <output>/screenshots/.
  3. State persists in <output>/state.json (resumable).

Reads flow.json "videos[]" entries:
  { "id": "clip-hook", "prompt": "...", "duration": "4s|6s|8s",
    "reference_image": "anchor-hero-lens" }   # optional state.json image id

Usage:
  python3 run_videos.py --config flow.json --output ./out \
      [--only VIDEO_ID] [--chrome-port 9222] [--batch x1|x2|x3|x4]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from browser_harness import FlowHarness, get_ws_url

VIDEO_MODEL = "Veo 3.1 - Lite [Lower Priority]"


def fail(msg: str, screenshot: Path | None = None) -> None:
    print(json.dumps({"ok": False, "error": msg,
                      "screenshot": str(screenshot) if screenshot else None},
                     ensure_ascii=False))
    sys.exit(1)


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"images": {}, "clips": {}, "videos": {}}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--only")
    ap.add_argument("--chrome-port", type=int, default=9222)
    ap.add_argument("--batch", choices=["x1", "x2", "x3", "x4"], default="x4",
                    help="variants per prompt (default x4 — 0 credits makes "
                         "4-for-1 the rational choice; pick best, discard rest)")
    ap.add_argument("--timeout", type=float, default=2400,
                    help="per-video wait in seconds (lower-priority queue can be slow)")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    videos = cfg.get("videos", [])
    if not videos:
        fail("flow.json has no videos[] entries")
    if args.only:
        videos = [v for v in videos if v["id"] == args.only]
        if not videos:
            fail(f"no video with id {args.only}")

    out_dir = Path(args.output)
    screenshots = out_dir / "screenshots"
    state_path = out_dir / "state.json"
    state = load_state(state_path)

    videos = [v for v in videos
              if not (state.get("videos", {}).get(v["id"], {}).get("status") == "done")]
    if not videos:
        print(json.dumps({"ok": True, "done": True, "message": "all videos already done"}, ensure_ascii=False))
        return

    ws_url = get_ws_url(args.chrome_port, cfg.get("flow_url", "https://flow.google.com"))
    harness = FlowHarness(ws_url, screenshots)
    try:
        state.setdefault("videos", {})

        # ---- configure settings once: Video mode + Lite [Lower Priority] ----
        harness._open_settings_panel()
        harness._click_settings_toggle("Video")
        harness._open_model_menu_and_select(VIDEO_MODEL)
        aspect = cfg.get("aspect_ratio", "9:16")
        if aspect in ("9:16", "16:9"):
            harness._click_settings_toggle(aspect)
        # verify 0-credit BEFORE anything else
        credits_line = harness._read_credits_line()
        if "0 credits" not in credits_line and "0크레딧" not in credits_line:
            shot = harness.screenshot("fail_credits_gate")
            fail(f"settings panel shows '{credits_line}' — expected 0 credits. "
                 f"Model '{VIDEO_MODEL}' may have been changed by Google. Aborting "
                 f"before any generation.", shot)

        for video in videos:
            vid = video["id"]
            prompt = video["prompt"]
            duration = video.get("duration", "8s")
            if duration not in ("4s", "6s", "8s"):
                fail(f"videos[] {vid}: duration must be 4s|6s|8s (Lite only supports these)")
            harness._click_settings_toggle(duration)
            # batch: x4 by default — 0 credits means 4 variants for free;
            # pick the best one offline, discard the rest
            harness._click_settings_toggle(args.batch)
            n_expected = int(args.batch[1])

            # credits gate with the final duration & batch toggles active
            credits_line = harness._read_credits_line()
            if "0 credits" not in credits_line and "0크레딧" not in credits_line:
                shot = harness.screenshot(f"fail_credits_{vid}")
                fail(f"credits gate tripped for {vid} with {args.batch}: '{credits_line}'", shot)
            harness._close_settings_panel()

            # optional reference image (from state.json images)
            ref_id = video.get("reference_image")
            if ref_id:
                ref = state["images"].get(ref_id)
                if not ref or ref.get("status") != "done" or not ref.get("file"):
                    fail(f"videos[] {vid}: reference_image '{ref_id}' not generated yet")
                harness._attach_reference_image(Path(ref["file"]))

            # clear + type prompt
            harness._type_prompt(prompt)

            # count videos before generating
            before = harness._count_videos()
            harness._click_create()

            # wait for N NEW video elements (x4 batch → 4 variants)
            results = harness._wait_for_new_videos(before, n=n_expected,
                                                   timeout=args.timeout)
            if not results:
                shot = harness.screenshot(f"fail_timeout_{vid}")
                state["videos"][vid] = {"status": "timeout", "prompt": prompt}
                save_state(state_path, state)
                fail(f"timed out waiting for video {vid} (queue can be slow; "
                     f"retry with --only {vid})", shot)

            vid_dir = out_dir / "videos"
            vid_dir.mkdir(exist_ok=True)
            files = []
            for i, (url, w, h, dur) in enumerate(results):
                suffix = f"-v{i + 1}" if len(results) > 1 else ""
                dest = vid_dir / f"{vid}{suffix}.mp4"
                if url:
                    harness.download_asset(url, dest)
                    files.append(str(dest))
                else:
                    files.append(None)
            state["videos"][vid] = {
                "status": "done", "prompt": prompt, "model": VIDEO_MODEL,
                "duration": duration, "batch": args.batch,
                "variants": [
                    {"file": f, "url": u, "spec": f"{w}x{h}, {d}s"}
                    for f, (u, w, h, d) in zip(files, results)
                ],
                "credits_charged": 0,
            }
            save_state(state_path, state)
            print(json.dumps({"ok": True, "video": vid, "variants": len(results),
                              "files": [f for f in files if f]},
                             ensure_ascii=False), flush=True)
            harness._open_settings_panel()  # re-open for the next iteration

        print(json.dumps({"ok": True, "done": True, "generated": len(videos)}, ensure_ascii=False))
    finally:
        harness.close()


if __name__ == "__main__":
    main()