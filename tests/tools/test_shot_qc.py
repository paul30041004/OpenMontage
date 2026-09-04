import json
import tempfile
from pathlib import Path
from PIL import Image

from tools.analysis.shot_qc import ShotQC


def test_shot_qc_evaluation_and_retake():
    tool = ShotQC()
    assert tool.name == "shot_qc"
    assert tool.capability == "analysis"

    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "artifacts").mkdir()
        (p / "assets" / "anchors").mkdir(parents=True)
        (p / "assets" / "video").mkdir(parents=True)

        anchor_img = p / "assets" / "anchors" / "hero_anchor.png"
        Image.new("RGB", (64, 64), color=(220, 110, 40)).save(anchor_img)

        shot1_img = p / "assets" / "video" / "sc1.png"
        Image.new("RGB", (64, 64), color=(215, 112, 45)).save(shot1_img)

        shot2_img = p / "assets" / "video" / "sc2.png"
        Image.new("RGB", (64, 64), color=(20, 30, 220)).save(shot2_img)

        cc_data = {
            "version": "1.0",
            "characters": [
                {"id": "char_protagonist", "reference_image_paths": [str(anchor_img)]}
            ],
        }
        with open(p / "artifacts" / "character_consistency.json", "w") as f:
            json.dump(cc_data, f)

        sp_data = {
            "scenes": [
                {"id": "sc_1", "character_ids": ["char_protagonist"]},
                {"id": "sc_2", "character_ids": ["char_protagonist"]},
            ]
        }
        with open(p / "artifacts" / "scene_plan.json", "w") as f:
            json.dump(sp_data, f)

        manifest_data = {
            "version": "1.0",
            "assets": [
                {"id": "ast_1", "scene_id": "sc_1", "type": "image", "path": str(shot1_img)},
                {"id": "ast_2", "scene_id": "sc_2", "type": "image", "path": str(shot2_img)},
            ],
        }
        with open(p / "artifacts" / "asset_manifest.json", "w") as f:
            json.dump(manifest_data, f)

        res = tool.execute({
            "operation": "evaluate_manifest",
            "project_dir": str(p),
            "similarity_threshold": 0.70,
            "auto_retake": True,
        })

        assert res.success is True
        data = res.data
        assert "report" in data
        assert data["report"]["checks"]["schema_valid"] is True
        assert data["retakes_scheduled_count"] == 1

        retake_file = p / "artifacts" / "retake_requests.json"
        assert retake_file.is_file()
        with open(retake_file) as rf:
            retakes = json.load(rf)
            assert len(retakes) == 1
            assert retakes[0]["scene_id"] == "sc_2"
            assert retakes[0]["status"] == "pending"
