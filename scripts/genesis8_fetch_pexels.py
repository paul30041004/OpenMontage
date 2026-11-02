"""Fetch Pexels stock visuals for the Genesis 8 short (portrait 9:16)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.checkpoint import write_checkpoint
from tools.tool_registry import registry

P = Path("projects")
pid = "genesis-8-after-the-rain"
ROOT = Path(".")
plan = json.loads((P / pid / "artifacts/scene_plan.json").read_text())

IMG_QUERIES = {
    "sc02": "sunlight through clouds calm sea",
    "sc03": "noahs ark wooden boat mountain",
    "sc04": "ocean horizon boat deck",
    "sc05": "elderly man portrait grey beard",
    "sc06": "crow bird flying sky",
    "sc07": "white dove flying",
    "sc08": "bird hands gentle light",
    "sc10": "olive branch dew closeup",
    "sc11": "man tears emotional face closeup",
    "sc12": "mountains rising above sea mist",
    "sc13": "stone pile altar fire",
    "sc14": "smoke rising dawn sky",
    "sc15": "sunlight pouring wheat field",
    "sc16": "wheat hand farmer grain",
    "sc17": "person window rain glass",
    "sc18": "morning sunlight window room person",
    "sc19": "dove flying sunrise silhouette",
    "sc20": "olive leaf hand sunlight",
}

VID_QUERIES = {
    "sc01": "storm clouds rain dark",
    "sc09": "white dove flying slow motion",
}

registry.discover()
img = registry._tools["pexels_image"]
vid = registry._tools["pexels_video"]

img_dir = P / pid / "assets/images"
vid_dir = P / pid / "assets/video"
img_dir.mkdir(parents=True, exist_ok=True)
vid_dir.mkdir(parents=True, exist_ok=True)

manifest = {}

for scene_id, query in IMG_QUERIES.items():
    dst = img_dir / f"{scene_id}.jpg"
    if dst.exists():
        manifest[scene_id] = {"kind": "image", "query": query, "path": str(dst), "source": "pexels_image"}
        continue
    r = img.execute({"query": query, "orientation": "portrait", "per_page": 6, "download_size": "large2x", "output_path": str(dst)})
    if r.success and r.data.get("path"):
        manifest[scene_id] = {
            "kind": "image", "query": query, "path": r.data["path"],
            "source": "pexels_image",
            "photographer": r.data.get("photographer"), "url": r.data.get("url"),
        }
        print(f"[img-ok] {scene_id} <- {r.data.get('photographer')}")
    else:
        print(f"[img-MISS] {scene_id} '{query}': {r.error if not r.success else r.data}")

    write_checkpoint(P, pid, "assets", "in_progress", {},
        pipeline_type="short-form-factory",
        metadata={"partial_progress": {"completed_visuals": sorted(manifest.keys())}})

for scene_id, query in VID_QUERIES.items():
    dst = vid_dir / f"{scene_id}.mp4"
    if dst.exists():
        manifest[scene_id] = {"kind": "video", "query": query, "path": str(dst), "source": "pexels_video"}
        continue
    r = vid.execute({"query": query, "orientation": "portrait", "per_page": 6, "preferred_quality": "hd", "output_path": str(dst)})
    if r.success and r.data.get("path"):
        manifest[scene_id] = {
            "kind": "video", "query": query, "path": r.data["path"],
            "source": "pexels_video", "url": r.data.get("url"),
        }
        print(f"[vid-ok] {scene_id}")
    else:
        print(f"[vid-MISS] {scene_id} '{query}': {r.error if not r.success else r.data}")

    write_checkpoint(P, pid, "assets", "in_progress", {},
        pipeline_type="short-form-factory",
        metadata={"partial_progress": {"completed_visuals": sorted(manifest.keys())}})

(P / pid / "artifacts/pexels_picks.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"saved {len(manifest)} picks")
