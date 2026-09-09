#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for MediaConverter: 3-Way Media Bridge for MuseScore, Synthesizer V Pro, and FreeShow.
"""

import os
import sys
import json
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.media_converter import MediaConverter, pitch_to_midi, midi_to_pitch, SV_BEAT_BLICKS

SAMPLE_MUSICXML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1">
      <part-name>Vocal</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <direction placement="above">
        <sound tempo="100"/>
      </direction>
      <!-- Note 1: C4 quarter note '은' -->
      <note>
        <pitch>
          <step>C</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>은</text>
        </lyric>
      </note>
      <!-- Note 2: D4 quarter note '혜' -->
      <note>
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>혜</text>
        </lyric>
      </note>
      <!-- Note 3: E4 quarter note '아' -->
      <note>
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>아</text>
        </lyric>
      </note>
      <!-- Note 4: F4 quarter note '니' -->
      <note>
        <pitch>
          <step>F</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>니</text>
        </lyric>
      </note>
    </measure>
    <measure number="2">
      <!-- Note 5: G4 half note '면' -->
      <note>
        <pitch>
          <step>G</step>
          <octave>4</octave>
        </pitch>
        <duration>8</duration>
        <lyric>
          <text>면</text>
        </lyric>
      </note>
      <!-- Rest: half rest -->
      <note>
        <rest/>
        <duration>8</duration>
      </note>
    </measure>
    <measure number="3">
      <!-- Note 6: A4 quarter note '십' -->
      <note>
        <pitch>
          <step>A</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>십</text>
        </lyric>
      </note>
      <!-- Note 7: B4 quarter note '자' -->
      <note>
        <pitch>
          <step>B</step>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric>
          <text>자</text>
        </lyric>
      </note>
      <!-- Note 8: C5 half note '가' -->
      <note>
        <pitch>
          <step>C</step>
          <octave>5</octave>
        </pitch>
        <duration>8</duration>
        <lyric>
          <text>가</text>
        </lyric>
      </note>
    </measure>
  </part>
</score-partwise>
"""


def test_pitch_midi_conversion():
    assert pitch_to_midi("C", 4, 0) == 60
    assert pitch_to_midi("A", 4, 0) == 69
    assert pitch_to_midi("C", 5, 0) == 72
    assert pitch_to_midi("F", 4, 1) == 66  # F#4
    assert pitch_to_midi("B", 3, -1) == 58  # Bb3

    step, octv, alt = midi_to_pitch(60)
    assert step == "C" and octv == 4 and alt == 0

    step, octv, alt = midi_to_pitch(69)
    assert step == "A" and octv == 4 and alt == 0


def test_musicxml_to_svp():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "test.musicxml")
        svp_path = os.path.join(tmpdir, "test.svp")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        converter.musicxml_to_svp(xml_path, svp_path)

        assert os.path.exists(svp_path)
        with open(svp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["version"] == 153
        assert data["time"]["tempo"][0]["bpm"] == 100.0
        track = data["tracks"][0]
        notes = track["mainGroup"]["notes"]
        assert len(notes) == 8  # 8 notes (rest is skipped in notes list, onset advanced)

        # Check lyrics
        assert notes[0]["lyrics"] == "은"
        assert notes[0]["pitch"] == 60
        assert notes[0]["duration"] == SV_BEAT_BLICKS

        assert notes[1]["lyrics"] == "혜"
        assert notes[1]["pitch"] == 62

        # Check rest timing impact:
        # Note 4 ('면') starts at onset 4 * SV_BEAT_BLICKS = 2,822,400,000, duration 2 beats (8 divs)
        # Then half rest (8 divs = 2 beats). So Note 5 ('십') should start after 8 beats total = onset 8 * SV_BEAT_BLICKS
        assert notes[4]["lyrics"] == "면"
        assert notes[4]["duration"] == 2 * SV_BEAT_BLICKS
        assert notes[5]["lyrics"] == "십"
        assert notes[5]["onset"] == 8 * SV_BEAT_BLICKS


def test_svp_to_freeshow():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "test.musicxml")
        svp_path = os.path.join(tmpdir, "test.svp")
        fs_path = os.path.join(tmpdir, "test_fs.json")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        converter.musicxml_to_svp(xml_path, svp_path)
        converter.svp_to_freeshow(svp_path, fs_path, lines_per_slide=2)

        assert os.path.exists(fs_path)
        with open(fs_path, "r", encoding="utf-8") as f:
            fs_data = json.load(f)

        slides = fs_data["slides"]
        assert len(slides) >= 1
        # Check Korean preservation
        all_text = " ".join(s["text"] for s in slides)
        assert "은혜아니면" in all_text or "은" in all_text
        assert "십자가" in all_text or "십" in all_text


def test_freeshow_to_musicxml_reverse_update():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "test.musicxml")
        fs_path = os.path.join(tmpdir, "updated_fs.json")
        out_xml_path = os.path.join(tmpdir, "updated.musicxml")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        # Create updated FreeShow with revised lyrics: 8 syllables
        # Original: 은 혜 아 니 면 (rest) 십 자 가
        # Updated:  주 의 보 혈 능 력 (rest) 사 랑 해
        custom_fs = {
            "version": "1.0.0",
            "type": "show",
            "slides": [
                {
                    "id": "slide_1",
                    "lines": ["주의 보혈", "능력 사랑해"],
                    "text": "주의 보혈\n능력 사랑해"
                }
            ]
        }
        with open(fs_path, "w", encoding="utf-8") as f:
            json.dump(custom_fs, f, ensure_ascii=False)

        converter.freeshow_to_musicxml(fs_path, xml_path, out_xml_path)

        assert os.path.exists(out_xml_path)
        tree = ET.parse(out_xml_path)
        root = tree.getroot()

        lyric_texts = [el.text for el in root.iter("text") if el.text]
        # Syllables should be: 주, 의, 보, 혈, 능, 력, 사, 랑 (8 syllables)
        assert lyric_texts[0] == "주"
        assert lyric_texts[1] == "의"
        assert lyric_texts[2] == "보"
        assert lyric_texts[3] == "혈"
        assert lyric_texts[4] == "능"


def test_bridge_all():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "score.musicxml")
        outdir = os.path.join(tmpdir, "output")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        res = converter.bridge_all(xml_path, outdir)
        assert os.path.exists(res["svp"])
        assert os.path.exists(res["freeshow"])


def test_svp_to_musicxml():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "test.musicxml")
        svp_path = os.path.join(tmpdir, "test.svp")
        out_xml = os.path.join(tmpdir, "from_svp.musicxml")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        converter.musicxml_to_svp(xml_path, svp_path)
        converter.svp_to_musicxml(svp_path, out_xml)

        assert os.path.exists(out_xml)
        tree = ET.parse(out_xml)
        root = tree.getroot()
        notes = list(root.iter("note"))
        assert len(notes) > 0


def test_freeshow_to_svp():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "test.musicxml")
        svp_path = os.path.join(tmpdir, "test.svp")
        fs_path = os.path.join(tmpdir, "test_fs.json")
        out_svp = os.path.join(tmpdir, "updated.svp")

        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_MUSICXML)

        converter.musicxml_to_svp(xml_path, svp_path)

        custom_fs = {
            "version": "1.0.0",
            "type": "show",
            "slides": [
                {
                    "id": "slide_1",
                    "lines": ["평화 평화", "하늘의 은혜"]
                }
            ]
        }
        with open(fs_path, "w", encoding="utf-8") as f:
            json.dump(custom_fs, f, ensure_ascii=False)

        converter.freeshow_to_svp(fs_path, svp_path, out_svp)
        assert os.path.exists(out_svp)
        with open(out_svp, "r", encoding="utf-8") as f:
            data = json.load(f)

        notes = data["tracks"][0]["mainGroup"]["notes"]
        assert notes[0]["lyrics"] == "평"
        assert notes[1]["lyrics"] == "화"


def test_mxl_format_and_multi_part():
    import zipfile
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        mxl_path = os.path.join(tmpdir, "string_quartet.mxl")
        svp_path = os.path.join(tmpdir, "vocal.svp")

        # Create multi-part XML (Violin 1 and Violin 2)
        multi_part_xml = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Violin 1</part-name></score-part>
    <score-part id="P2"><part-name>Violin 2</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>4</divisions></attributes>
      <note><pitch><step>C</step><octave>5</octave></pitch><duration>4</duration></note>
      <note><pitch><step>B</step><octave>4</octave></pitch><duration>4</duration></note>
    </measure>
  </part>
  <part id="P2">
    <measure number="1">
      <attributes><divisions>4</divisions></attributes>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>4</duration></note>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>4</duration></note>
    </measure>
  </part>
</score-partwise>"""

        # Package into .mxl (zip with META-INF/container.xml)
        with zipfile.ZipFile(mxl_path, "w") as z:
            container = """<?xml version="1.0" encoding="UTF-8"?>
<container><rootfiles><rootfile full-path="score.xml"/></rootfiles></container>"""
            z.writestr("META-INF/container.xml", container)
            z.writestr("score.xml", multi_part_xml)

        # Convert to SVP with lyrics override
        converter.musicxml_to_svp(
            mxl_path,
            svp_path,
            bpm=100.0,
            part_id="P1",
            lyrics_text="기쁨"
        )

        assert os.path.exists(svp_path)
        with open(svp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        notes = data["tracks"][0]["mainGroup"]["notes"]
        assert len(notes) == 2
        assert notes[0]["pitch"] == 72  # C5
        assert notes[0]["lyrics"] == "기"
        assert notes[1]["pitch"] == 71  # B4
        assert notes[1]["lyrics"] == "쁨"


def test_multi_verse_and_lyric_cleaning():
    converter = MediaConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = os.path.join(tmpdir, "verse_test.xml")
        svp_v1_path = os.path.join(tmpdir, "v1.svp")
        svp_v2_path = os.path.join(tmpdir, "v2.svp")
        fs_path = os.path.join(tmpdir, "subtitles.json")

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Vocal</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>4</divisions></attributes>
      <note>
        <pitch><step>D</step><octave>5</octave></pitch>
        <duration>4</duration>
        <lyric number="1"><text>1.기</text></lyric>
        <lyric number="2"><text>2.구</text></lyric>
      </note>
      <note>
        <pitch><step>C</step><octave>5</octave></pitch>
        <duration>4</duration>
      </note>
      <note>
        <pitch><step>B</step><octave>4</octave></pitch>
        <duration>4</duration>
        <lyric number="1"><text>쁘</text></lyric>
        <lyric number="2"><text>세</text></lyric>
      </note>
    </measure>
  </part>
</score-partwise>"""
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)

        # Verse 1 test
        converter.musicxml_to_svp(xml_path, svp_v1_path, verse=1)
        with open(svp_v1_path, "r", encoding="utf-8") as f:
            v1_data = json.load(f)
        v1_notes = v1_data["tracks"][0]["mainGroup"]["notes"]
        assert v1_notes[0]["lyrics"] == "기"
        assert v1_notes[1]["lyrics"] == "-"
        assert v1_notes[2]["lyrics"] == "쁘"

        # Verse 2 test
        converter.musicxml_to_svp(xml_path, svp_v2_path, verse=2)
        with open(svp_v2_path, "r", encoding="utf-8") as f:
            v2_data = json.load(f)
        v2_notes = v2_data["tracks"][0]["mainGroup"]["notes"]
        assert v2_notes[0]["lyrics"] == "구"
        assert v2_notes[1]["lyrics"] == "-"
        assert v2_notes[2]["lyrics"] == "세"

        # FreeShow test
        converter.musicxml_to_freeshow(xml_path, fs_path, verse=1)
        with open(fs_path, "r", encoding="utf-8") as f:
            fs_data = json.load(f)
        all_fs_text = "".join(line for s in fs_data["slides"] for line in s["lines"])
        assert "1." not in all_fs_text
        assert "기쁘" in all_fs_text


def test_satb_and_octave_guard():
    from scripts.media_converter import apply_octave_guard, VOCAL_RANGES
    # Test octave guard
    # Soprano (57-86): C7 = 96 should transpose down to C6 = 84 or C5 = 72
    guarded_soprano = apply_octave_guard(96, VOCAL_RANGES["soprano"])
    assert 57 <= guarded_soprano <= 86
    # Bass (38-65): C1 = 24 should transpose up to C2 = 36 or C3 = 48
    guarded_bass = apply_octave_guard(24, VOCAL_RANGES["bass"])
    assert 38 <= guarded_bass <= 65

    # Test SATB export with tong115 mxl
    converter = MediaConverter()
    mxl_sample = "assets/tong115janggippeuda-guju-osyeossnehyeon-ag4jungju.mxl"
    if os.path.exists(mxl_sample):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_satb = os.path.join(tmpdir, "satb.svp")
            res = converter.musicxml_to_satb_svp(mxl_sample, out_satb, bpm=100.0, verse=1, add_breath=True)
            assert os.path.exists(out_satb)
            with open(out_satb, "r", encoding="utf-8") as f:
                satb_data = json.load(f)
            assert len(satb_data["tracks"]) == 4
            assert "SOLARIA II" in satb_data["tracks"][0]["name"]
            assert "ASTERIAN II" in satb_data["tracks"][3]["name"]


if __name__ == "__main__":
    test_pitch_midi_conversion()
    test_musicxml_to_svp()
    test_svp_to_musicxml()
    test_svp_to_freeshow()
    test_freeshow_to_musicxml_reverse_update()
    test_freeshow_to_svp()
    test_mxl_format_and_multi_part()
    test_multi_verse_and_lyric_cleaning()
    test_satb_and_octave_guard()
    test_bridge_all()
    print("✨ All unit tests passed successfully!")
