#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaConverter: 3-Way Media Bridge for MuseScore (.musicxml), Synthesizer V Pro (.svp), and FreeShow (.json)
Optimized for macOS Apple Silicon (M-series) / universal Python 3 environments.

Features:
1. MusicXML <-> Synthesizer V Pro (.svp):
   - Pitch Step/Octave/Alter <-> MIDI note (0-127) mapping
   - MusicXML duration (divisions) <-> Synth V blicks (705,600,000 blicks / beat)
   - Monophonic singing line extraction, rest handling, onset alignment
   - Lyrics <-> note lyrics mapping (missing lyrics mapped to '-')
2. MusicXML / SVP -> FreeShow (.json):
   - Smart wrapper: filters '-' and blank tokens, aggregates syllables into phrases
   - 2-line/phrase layout per slide packaging with timestamps
   - Generates both clean presentation schema and native FreeShow item structure
3. FreeShow -> MusicXML / SVP (Reverse Lyric Update):
   - Preserves musical pitch, timing, and rests
   - Sequentially updates vocal text tokens from edited FreeShow slides
4. Full UTF-8 enforcement to guarantee zero Korean character corruption
"""

import os
import sys
import json
import uuid
import re
import zipfile
import argparse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple

# Synthesizer V Pro constant: 1 beat (quarter note in 4/4) = 705,600,000 blicks
SV_BEAT_BLICKS = 705600000

# Semitone offsets from C
NOTE_STEP_SEMITONES = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11
}

# Reverse mapping: semitone (0-11) -> (step, alter)
SEMITONE_TO_STEP = {
    0: ("C", 0),
    1: ("C", 1),
    2: ("D", 0),
    3: ("D", 1),
    4: ("E", 0),
    5: ("F", 0),
    6: ("F", 1),
    7: ("G", 0),
    8: ("G", 1),
    9: ("A", 0),
    10: ("A", 1),
    11: ("B", 0)
}


def pitch_to_midi(step: str, octave: int, alter: int = 0) -> int:
    """Converts MusicXML step, octave, and alter to MIDI note number (C4 = 60)."""
    step_upper = step.strip().upper()
    base = NOTE_STEP_SEMITONES.get(step_upper, 0)
    midi_num = (octave + 1) * 12 + base + alter
    return max(0, min(127, midi_num))


def midi_to_pitch(midi_num: int) -> Tuple[str, int, int]:
    """Converts MIDI note number to (step, octave, alter)."""
    midi_num = max(0, min(127, int(midi_num)))
    octave = (midi_num // 12) - 1
    semitone = midi_num % 12
    step, alter = SEMITONE_TO_STEP.get(semitone, ("C", 0))
    return step, octave, alter


def parse_musicxml_source(source_path: str) -> Tuple[ET.ElementTree, ET.Element]:
    """
    Parses uncompressed (.musicxml, .xml) or compressed (.mxl) MusicXML files.
    Returns (tree, root_element).
    """
    if source_path.endswith(".mxl") or zipfile.is_zipfile(source_path):
        with zipfile.ZipFile(source_path, "r") as z:
            xml_filename = None
            if "META-INF/container.xml" in z.namelist():
                try:
                    c_root = ET.fromstring(z.read("META-INF/container.xml"))
                    rootfile = c_root.find(".//rootfile[@full-path]")
                    if rootfile is not None and rootfile.get("full-path"):
                        xml_filename = rootfile.get("full-path")
                except Exception:
                    pass
            if not xml_filename:
                for name in z.namelist():
                    if (name.endswith(".xml") or name.endswith(".musicxml")) and not name.startswith("META-INF"):
                        xml_filename = name
                        break
            if not xml_filename:
                raise ValueError(f".mxl 압축 파일 내부에 유효한 MusicXML 파일이 없습니다: {source_path}")
            xml_content = z.read(xml_filename)
            root = ET.fromstring(xml_content)
            return ET.ElementTree(root), root
    else:
        tree = ET.parse(source_path)
        return tree, tree.getroot()


def get_target_part(root: ET.Element, part_id: Optional[str] = None) -> Tuple[str, str, ET.Element]:
    """
    Finds the target part in a multi-part score (e.g. string quartet, SATB choir).
    If part_id is not specified, selects the part with the most lyrics,
    or falls back to the first part (Part 1 / Violin 1 / Soprano).
    """
    part_names = {}
    for sp in root.findall(".//part-list/score-part"):
        pid = sp.get("id", "")
        pname_el = sp.find("part-name")
        pname = pname_el.text.strip() if (pname_el is not None and pname_el.text) else pid
        part_names[pid] = pname

    parts = root.findall(".//part")
    if not parts:
        return "P1", "Default", root

    if part_id is not None:
        target_str = str(part_id).strip().lower()
        for p in parts:
            pid = p.get("id", "")
            pname = part_names.get(pid, pid)
            if pid.lower() == target_str or pname.lower() == target_str:
                return pid, pname, p
        if target_str.isdigit():
            idx = int(target_str) - 1
            if 0 <= idx < len(parts):
                p = parts[idx]
                pid = p.get("id", "")
                return pid, part_names.get(pid, pid), p

    # Auto-detect: check which part has the most lyrics
    best_part = parts[0]
    best_lyric_count = -1
    for p in parts:
        lyric_count = len(p.findall(".//lyric"))
        if lyric_count > best_lyric_count:
            best_lyric_count = lyric_count
            best_part = p

    sel_id = best_part.get("id", "P1")
    sel_name = part_names.get(sel_id, sel_id)
    return sel_id, sel_name, best_part


def extract_note_lyric(note: ET.Element, verse: int = 1) -> Optional[str]:
    """
    Extracts lyric text from a note element for a specific verse (1-indexed).
    Cleans leading verse numbers (e.g. '1.기' -> '기', '2.구' -> '구').
    Returns None if no lyric is present for this verse or if lyric is empty.
    """
    lyrics = note.findall("lyric")
    if not lyrics:
        lyrics = note.findall(".//lyric")
    if not lyrics:
        return None

    target_lyric = None
    verse_str = str(verse)
    for l in lyrics:
        if l.get("number") == verse_str:
            target_lyric = l
            break

    if target_lyric is None:
        if len(lyrics) == 1 and lyrics[0].get("number") is None:
            target_lyric = lyrics[0]
        else:
            return None

    text_el = target_lyric.find("text")
    if text_el is not None and text_el.text:
        raw_text = text_el.text.strip()
        cleaned = re.sub(r"^\d+[\.\s]+", "", raw_text)
        return cleaned if cleaned else raw_text
    return None


VOCAL_RANGES = {
    "soprano": (57, 86),  # A3 - D6 (typical: C4~C6 = 60~84)
    "alto": (50, 77),     # D3 - F5 (typical: F3~D5 = 53~74)
    "tenor": (45, 72),    # A2 - C5 (typical: C3~A4 = 48~69)
    "bass": (38, 65),     # D2 - F4 (typical: E2~E4 = 40~64)
    "general": (45, 88),  # A2 - E6
}


def apply_octave_guard(pitch: int, vocal_range: Tuple[int, int]) -> int:
    """Clamps MIDI pitch into physically singable vocal range by transposing by octaves (+/-12)."""
    min_p, max_p = vocal_range
    while pitch < min_p and pitch + 12 <= 127:
        pitch += 12
    while pitch > max_p and pitch - 12 >= 0:
        pitch -= 12
    return max(0, min(127, pitch))


SATB_PRESETS = [
    {"role": "soprano", "name": "Soprano (SOLARIA II)", "voice": "SOLARIA II", "color": "ff7895", "pan": -0.2},
    {"role": "alto", "name": "Alto (SAROS II)", "voice": "SAROS II", "color": "ff78c8", "pan": -0.1},
    {"role": "tenor", "name": "Tenor (Kevin 2)", "voice": "Kevin 2", "color": "78aaff", "pan": 0.1},
    {"role": "bass", "name": "Bass (ASTERIAN II)", "voice": "ASTERIAN II", "color": "7878ff", "pan": 0.2},
]


class MediaConverter:
    """3-Way Converter & Synchronizer between MusicXML, Synthesizer V Pro, and FreeShow."""

    def __init__(self, default_bpm: float = 120.0, default_meter: Tuple[int, int] = (4, 4)):
        self.default_bpm = default_bpm
        self.default_meter = default_meter

    def _extract_notes_from_part_el(
        self,
        target_part: ET.Element,
        divisions: int,
        verse: int = 1,
        external_syllables: Optional[List[str]] = None,
        vocal_role: Optional[str] = None,
        add_breath: bool = False,
        vibrato_amount: float = 0.65,
        target_staff: Optional[str] = "1",
        target_voice: Optional[str] = "1"
    ) -> List[Dict[str, Any]]:
        has_any_score_lyrics = target_part.find(".//lyric") is not None
        staves = set(n.find('staff').text for n in target_part.findall('.//note') if n.find('staff') is not None)
        voices = set(n.find('voice').text for n in target_part.findall('.//note') if n.find('voice') is not None)
        is_multitrack = len(staves) > 1 or len(voices) > 1

        vocal_range = VOCAL_RANGES.get(vocal_role.lower()) if vocal_role else None

        notes_data: List[Dict[str, Any]] = []
        current_time_blicks = 0
        last_note_end_blicks = 0
        ext_syl_idx = 0

        for note in target_part.iter("note"):
            if is_multitrack:
                st = note.find("staff")
                v = note.find("voice")
                if st is not None and target_staff and st.text != target_staff:
                    continue
                if v is not None and target_voice and v.text != target_voice:
                    continue

            if note.find("grace") is not None:
                continue

            duration_el = note.find("duration")
            raw_duration = int(duration_el.text.strip()) if (duration_el is not None and duration_el.text) else divisions
            duration_blicks = int(round((raw_duration / divisions) * SV_BEAT_BLICKS))

            is_chord = note.find("chord") is not None
            note_onset = current_time_blicks - duration_blicks if is_chord else current_time_blicks

            if note.find("rest") is not None:
                if not is_chord:
                    current_time_blicks += duration_blicks
                continue

            # Extract Pitch
            step_el = note.find(".//pitch/step")
            octave_el = note.find(".//pitch/octave")
            alter_el = note.find(".//pitch/alter")

            if step_el is not None and octave_el is not None:
                step = step_el.text.strip() if step_el.text else "C"
                octave = int(octave_el.text.strip()) if octave_el.text else 4
                alter = int(alter_el.text.strip()) if (alter_el is not None and alter_el.text) else 0
                midi_pitch = pitch_to_midi(step, octave, alter)
            else:
                midi_pitch = 60

            # Vocal Range Octave Guard
            if vocal_range is not None:
                midi_pitch = apply_octave_guard(midi_pitch, vocal_range)

            # Natural Breath Sound (Inhalation 'br') Insertion
            if add_breath and not is_chord and last_note_end_blicks > 0:
                gap_blicks = note_onset - last_note_end_blicks
                if gap_blicks >= int(SV_BEAT_BLICKS * 0.75):
                    breath_dur = min(int(SV_BEAT_BLICKS * 0.25), int(gap_blicks / 2))
                    breath_onset = note_onset - breath_dur
                    notes_data.append({
                        "musicalType": "singing",
                        "onset": int(breath_onset),
                        "duration": int(breath_dur),
                        "lyrics": "br",
                        "phonemes": "br",
                        "accent": "",
                        "pitch": int(midi_pitch),
                        "detune": 0,
                        "instantMode": True,
                        "attributes": {"evenSyllableDuration": True, "vibratoDepth": 0.0},
                        "systemAttributes": {"evenSyllableDuration": True},
                        "pitchTakes": {"activeTakeId": 0, "takes": [{"id": 0, "expr": 0.0, "liked": False}]},
                        "timbreTakes": {"activeTakeId": 0, "takes": [{"id": 0, "expr": 0.0, "liked": False}]}
                    })

            # Extract or Map Lyric
            orig_lyric = extract_note_lyric(note, verse=verse)
            lyric_text = "-"
            if external_syllables:
                if has_any_score_lyrics:
                    if orig_lyric is not None and ext_syl_idx < len(external_syllables):
                        lyric_text = external_syllables[ext_syl_idx]
                        ext_syl_idx += 1
                    else:
                        lyric_text = "-"
                else:
                    if ext_syl_idx < len(external_syllables):
                        lyric_text = external_syllables[ext_syl_idx]
                        ext_syl_idx += 1
                    else:
                        lyric_text = "-"
            else:
                if orig_lyric is not None:
                    lyric_text = orig_lyric

            # Vibrato & Pitch Takes expression modeling
            vib_depth = vibrato_amount if duration_blicks >= int(SV_BEAT_BLICKS * 0.75) else 0.15

            svp_note = {
                "musicalType": "singing",
                "onset": int(note_onset),
                "duration": int(duration_blicks),
                "lyrics": lyric_text,
                "phonemes": "",
                "accent": "",
                "pitch": int(midi_pitch),
                "detune": 0,
                "instantMode": True,
                "attributes": {
                    "evenSyllableDuration": True,
                    "vibratoDepth": float(vib_depth),
                    "vibratoFrequency": 5.5
                },
                "systemAttributes": {"evenSyllableDuration": True},
                "pitchTakes": {"activeTakeId": 0, "takes": [{"id": 0, "expr": 0.65, "liked": False}]},
                "timbreTakes": {"activeTakeId": 0, "takes": [{"id": 0, "expr": 0.0, "liked": False}]}
            }
            notes_data.append(svp_note)
            last_note_end_blicks = note_onset + duration_blicks

            if not is_chord:
                current_time_blicks += duration_blicks

        return notes_data

    # =========================================================================
    # 1. MusicXML -> Synthesizer V Pro (.svp)
    # =========================================================================
    def musicxml_to_svp(
        self,
        xml_path: str,
        output_svp_path: str,
        bpm: Optional[float] = None,
        part_id: Optional[str] = None,
        lyrics_text: Optional[str] = None,
        verse: int = 1,
        vocal_role: Optional[str] = None,
        add_breath: bool = False
    ) -> Dict[str, Any]:
        """
        Converts MusicXML (.musicxml or .mxl) to Synthesizer V Pro (.svp) project JSON.
        Accurately translates pitch, duration, rests, and lyrics.
        Supports multi-part scores (e.g. String Quartet) and external lyrics mapping.
        """
        tree, root = parse_musicxml_source(xml_path)

        # Multi-part detection
        part_id_found, part_name_found, target_part = get_target_part(root, part_id)
        all_parts = root.findall(".//part")
        if len(all_parts) > 1:
            print(f"ℹ️ 다중 파트 악보 감지 (총 {len(all_parts)}개 파트 중 '{part_id_found}: {part_name_found}' 선택됨)")

        # Parse global attributes (divisions, meter, tempo)
        divisions = 1
        div_el = target_part.find(".//attributes/divisions")
        if div_el is None:
            div_el = root.find(".//attributes/divisions")
        if div_el is not None and div_el.text:
            divisions = max(1, int(div_el.text.strip()))

        tempo = bpm if bpm is not None else self.default_bpm
        sound_el = target_part.find(".//sound[@tempo]")
        if sound_el is None:
            sound_el = root.find(".//sound[@tempo]")
        if sound_el is not None and sound_el.get("tempo") and bpm is None:
            try:
                tempo = float(sound_el.get("tempo"))
            except ValueError:
                pass

        meter_num, meter_den = self.default_meter
        beats_el = target_part.find(".//attributes/time/beats")
        if beats_el is None:
            beats_el = root.find(".//attributes/time/beats")
        beat_type_el = target_part.find(".//attributes/time/beat-type")
        if beat_type_el is None:
            beat_type_el = root.find(".//attributes/time/beat-type")
        if beats_el is not None and beat_type_el is not None:
            try:
                meter_num = int(beats_el.text.strip())
                meter_den = int(beat_type_el.text.strip())
            except (ValueError, AttributeError):
                pass

        # Prepare external lyrics mapping if provided
        external_syllables: List[str] = []
        if lyrics_text:
            for char in lyrics_text:
                if not char.isspace():
                    external_syllables.append(char)

        # Extract notes using modular helper
        notes_data = self._extract_notes_from_part_el(
            target_part,
            divisions=divisions,
            verse=verse,
            external_syllables=external_syllables if external_syllables else None,
            vocal_role=vocal_role,
            add_breath=add_breath
        )

        track_uuid = str(uuid.uuid4()).lower()

        # Synthesizer V Pro Project Template
        svp_project = {
            "version": 153,
            "time": {
                "meter": [{"index": 0, "numerator": meter_num, "denominator": meter_den}],
                "tempo": [{"position": 0, "bpm": float(tempo)}]
            },
            "library": [],
            "tracks": [
                {
                    "name": "Vocal Guide Track",
                    "dispColor": "ff7895",
                    "dispOrder": 0,
                    "renderEnabled": True,
                    "mixer": {
                        "gainDecibel": 0.0,
                        "pan": 0.0,
                        "mute": False,
                        "solo": False,
                        "display": True
                    },
                    "mainGroup": {
                        "name": "main",
                        "uuid": track_uuid,
                        "parameters": {},
                        "vocalModes": {},
                        "notes": notes_data
                    },
                    "mainRef": {
                        "groupID": track_uuid,
                        "blickAbsoluteBegin": 0,
                        "blickAbsoluteEnd": -1,
                        "blickOffset": 0,
                        "pitchOffset": 0,
                        "isInstrumental": False,
                        "systemPitchDelta": {"mode": "cubic", "points": []},
                        "database": {
                            "name": "",
                            "language": "korean",
                            "phoneset": "xsampa",
                            "languageOverride": "",
                            "phonesetOverride": "",
                            "backendType": "SVR2AI",
                            "version": "100"
                        },
                        "dictionary": "",
                        "voice": {
                            "vocalModeInherited": True,
                            "vocalModePreset": "",
                            "vocalModeParams": {}
                        }
                    },
                    "groups": []
                }
            ],
            "renderConfig": {
                "destination": "",
                "filename": "",
                "numChannels": 2,
                "aspirationFormat": "no",
                "bitDepth": 16,
                "sampleRate": 44100,
                "exportResolution": 1000
            }
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_svp_path)), exist_ok=True)
        with open(output_svp_path, "w", encoding="utf-8") as f:
            json.dump(svp_project, f, indent=2, ensure_ascii=False)

        print(f"✅ MusicXML ➡️ SVP 변환 완료: {output_svp_path} (노트 수: {len(notes_data)}, BPM: {tempo})")
        return svp_project

    # =========================================================================
    # 1-1. MusicXML -> SATB Multi-Track Synthesizer V Pro (.svp)
    # =========================================================================
    def musicxml_to_satb_svp(
        self,
        xml_path: str,
        output_svp_path: str,
        bpm: Optional[float] = None,
        verse: int = 1,
        add_breath: bool = True,
        lyrics_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Converts a choral, quartet, or ensemble score into a 4-track SATB (Soprano, Alto, Tenor, Bass)
        Synthesizer V Pro project. Automatically maps voice ranges, pans, and installed voice models.
        """
        tree, root = parse_musicxml_source(xml_path)
        all_parts = root.findall(".//part")
        if not all_parts:
            raise ValueError(f"악보 내에 유효한 파트가 없습니다: {xml_path}")

        # Global attributes
        first_part = all_parts[0]
        divisions = 1
        div_el = first_part.find(".//attributes/divisions")
        if div_el is None:
            div_el = root.find(".//attributes/divisions")
        if div_el is not None and div_el.text:
            divisions = max(1, int(div_el.text.strip()))

        tempo = bpm if bpm is not None else self.default_bpm
        sound_el = first_part.find(".//sound[@tempo]")
        if sound_el is None:
            sound_el = root.find(".//sound[@tempo]")
        if sound_el is not None and sound_el.get("tempo") and bpm is None:
            try:
                tempo = float(sound_el.get("tempo"))
            except ValueError:
                pass

        meter_num, meter_den = self.default_meter
        beats_el = first_part.find(".//attributes/time/beats")
        if beats_el is None:
            beats_el = root.find(".//attributes/time/beats")
        beat_type_el = first_part.find(".//attributes/time/beat-type")
        if beat_type_el is None:
            beat_type_el = root.find(".//attributes/time/beat-type")
        if beats_el is not None and beat_type_el is not None:
            try:
                meter_num = int(beats_el.text.strip())
                meter_den = int(beat_type_el.text.strip())
            except (ValueError, AttributeError):
                pass

        external_syllables: List[str] = []
        if lyrics_text:
            for char in lyrics_text:
                if not char.isspace():
                    external_syllables.append(char)

        tracks: List[Dict[str, Any]] = []
        total_notes = 0

        # Mapping strategies:
        # Case A: >= 4 separate parts (e.g. String Quartet, Choral SATB)
        # Case B: 1 part with multi-staff / multi-voice (e.g. Piano grand staff hymn reduction)
        satb_sources = []
        if len(all_parts) >= 4:
            satb_sources = [
                (all_parts[0], "1", "1", SATB_PRESETS[0]),
                (all_parts[1], "1", "1", SATB_PRESETS[1]),
                (all_parts[2], "1", "1", SATB_PRESETS[2]),
                (all_parts[3], "1", "1", SATB_PRESETS[3]),
            ]
        elif len(all_parts) == 1:
            satb_sources = [
                (all_parts[0], "1", "1", SATB_PRESETS[0]),
                (all_parts[0], "1", "2", SATB_PRESETS[1]),
                (all_parts[0], "2", "1", SATB_PRESETS[2]),
                (all_parts[0], "2", "2", SATB_PRESETS[3]),
            ]
        else:
            # 2 parts (e.g. Women / Men)
            satb_sources = [
                (all_parts[0], "1", "1", SATB_PRESETS[0]),
                (all_parts[0], "1", "2", SATB_PRESETS[1]),
                (all_parts[1], "1", "1", SATB_PRESETS[2]),
                (all_parts[1], "1", "2", SATB_PRESETS[3]),
            ]

        # Extract soprano syllables to inherit if harmony parts lack lyrics
        soprano_notes = self._extract_notes_from_part_el(
            satb_sources[0][0],
            divisions=divisions,
            verse=verse,
            external_syllables=external_syllables if external_syllables else None,
            vocal_role="soprano",
            add_breath=add_breath,
            target_staff=satb_sources[0][1],
            target_voice=satb_sources[0][2]
        )
        soprano_syllables = [n["lyrics"] for n in soprano_notes if n["lyrics"] not in ("-", "br")]

        for idx, (part_el, staff_val, voice_val, preset) in enumerate(satb_sources):
            role = preset["role"]
            vocal_name = preset["name"]
            color = preset["color"]
            pan = preset["pan"]
            voice_db = preset["voice"]

            if idx == 0:
                notes_data = soprano_notes
            else:
                notes_data = self._extract_notes_from_part_el(
                    part_el,
                    divisions=divisions,
                    verse=verse,
                    external_syllables=soprano_syllables if soprano_syllables else external_syllables,
                    vocal_role=role,
                    add_breath=add_breath,
                    target_staff=staff_val,
                    target_voice=voice_val
                )

            total_notes += len(notes_data)
            t_uuid = str(uuid.uuid4()).lower()
            track_entry = {
                "name": vocal_name,
                "dispColor": color,
                "dispOrder": idx,
                "renderEnabled": True,
                "mixer": {
                    "gainDecibel": 0.0,
                    "pan": float(pan),
                    "mute": False,
                    "solo": False,
                    "display": True
                },
                "mainGroup": {
                    "name": role,
                    "uuid": t_uuid,
                    "parameters": {},
                    "vocalModes": {},
                    "notes": notes_data
                },
                "mainRef": {
                    "groupID": t_uuid,
                    "blickAbsoluteBegin": 0,
                    "blickAbsoluteEnd": -1,
                    "blickOffset": 0,
                    "pitchOffset": 0,
                    "isInstrumental": False,
                    "systemPitchDelta": {"mode": "cubic", "points": []},
                    "database": {
                        "name": voice_db,
                        "language": "korean",
                        "phoneset": "xsampa",
                        "languageOverride": "",
                        "phonesetOverride": "",
                        "backendType": "SVR2AI",
                        "version": "100"
                    },
                    "dictionary": "",
                    "voice": {
                        "vocalModeInherited": True,
                        "vocalModePreset": "",
                        "vocalModeParams": {}
                    }
                },
                "groups": []
            }
            tracks.append(track_entry)

        svp_satb_project = {
            "version": 153,
            "time": {
                "meter": [{"index": 0, "numerator": meter_num, "denominator": meter_den}],
                "tempo": [{"position": 0, "bpm": float(tempo)}]
            },
            "library": [],
            "tracks": tracks,
            "renderConfig": {
                "destination": "",
                "filename": "",
                "numChannels": 2,
                "aspirationFormat": "no",
                "bitDepth": 16,
                "sampleRate": 44100,
                "exportResolution": 1000
            }
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_svp_path)), exist_ok=True)
        with open(output_svp_path, "w", encoding="utf-8") as f:
            json.dump(svp_satb_project, f, indent=2, ensure_ascii=False)

        print(f"🎉 SATB 4부 합창 SVP 생성 완료: {output_svp_path} (총 {len(tracks)}개 트랙, 전체 노트: {total_notes}, BPM: {tempo})")
        for t in tracks:
            print(f"  - [{t['name']}] 노트 {len(t['mainGroup']['notes'])}개, 팬 {t['mixer']['pan']}")
        return svp_satb_project

    # =========================================================================
    # 2. Synthesizer V Pro (.svp) -> MusicXML
    # =========================================================================
    def svp_to_musicxml(self, svp_path: str, output_xml_path: str, divisions: int = 480) -> str:
        """
        Converts Synthesizer V Pro (.svp) project JSON back to MusicXML.
        Preserves pitches, notes, timings, and lyrics.
        """
        with open(svp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract tempo and meter
        tempo = 120.0
        meter_num, meter_den = 4, 4
        time_info = data.get("time", {})
        if time_info.get("tempo") and len(time_info["tempo"]) > 0:
            tempo = float(time_info["tempo"][0].get("bpm", 120.0))
        if time_info.get("meter") and len(time_info["meter"]) > 0:
            meter_num = int(time_info["meter"][0].get("numerator", 4))
            meter_den = int(time_info["meter"][0].get("denominator", 4))

        # Extract notes from tracks
        tracks = data.get("tracks", [])
        notes: List[Dict[str, Any]] = []
        if tracks:
            track = tracks[0]
            if "mainGroup" in track and "notes" in track["mainGroup"]:
                notes = track["mainGroup"]["notes"]
            elif "notes" in track:
                notes = track["notes"]

        notes.sort(key=lambda n: n.get("onset", 0))

        # Build MusicXML Document
        score = ET.Element("score-partwise", version="3.1")
        part_list = ET.SubElement(score, "part-list")
        score_part = ET.SubElement(part_list, "score-part", id="P1")
        ET.SubElement(score_part, "part-name").text = "Vocal Lead"

        part = ET.SubElement(score, "part", id="P1")

        measure_length_blicks = int(meter_num * (4 / meter_den) * SV_BEAT_BLICKS)
        current_measure_num = 1
        current_measure_el = ET.SubElement(part, "measure", number=str(current_measure_num))

        # Measure attributes
        attrs = ET.SubElement(current_measure_el, "attributes")
        ET.SubElement(attrs, "divisions").text = str(divisions)
        time_el = ET.SubElement(attrs, "time")
        ET.SubElement(time_el, "beats").text = str(meter_num)
        ET.SubElement(time_el, "beat-type").text = str(meter_den)
        clef = ET.SubElement(attrs, "clef")
        ET.SubElement(clef, "sign").text = "G"
        ET.SubElement(clef, "line").text = "2"

        # Direction / Tempo
        direction = ET.SubElement(current_measure_el, "direction", placement="above")
        sound = ET.SubElement(direction, "sound", tempo=str(tempo))

        current_cursor_blicks = 0
        measure_start_blicks = 0

        for n in notes:
            onset = n.get("onset", 0)
            duration_blicks = n.get("duration", SV_BEAT_BLICKS)
            pitch_val = n.get("pitch", 60)
            lyric_val = n.get("lyrics", "-")

            # Insert rest if there is a gap between cursor and note onset
            if onset > current_cursor_blicks:
                rest_blicks = onset - current_cursor_blicks
                rest_divs = max(1, int(round((rest_blicks / SV_BEAT_BLICKS) * divisions)))
                rest_note = ET.SubElement(current_measure_el, "note")
                ET.SubElement(rest_note, "rest")
                ET.SubElement(rest_note, "duration").text = str(rest_divs)
                current_cursor_blicks = onset

            # Check measure boundary
            while current_cursor_blicks >= measure_start_blicks + measure_length_blicks:
                measure_start_blicks += measure_length_blicks
                current_measure_num += 1
                current_measure_el = ET.SubElement(part, "measure", number=str(current_measure_num))

            # Add singing note
            step, octave, alter = midi_to_pitch(pitch_val)
            note_divs = max(1, int(round((duration_blicks / SV_BEAT_BLICKS) * divisions)))

            note_el = ET.SubElement(current_measure_el, "note")
            pitch_el = ET.SubElement(note_el, "pitch")
            ET.SubElement(pitch_el, "step").text = step
            if alter != 0:
                ET.SubElement(pitch_el, "alter").text = str(alter)
            ET.SubElement(pitch_el, "octave").text = str(octave)

            ET.SubElement(note_el, "duration").text = str(note_divs)

            if lyric_val and lyric_val != "-":
                lyric_el = ET.SubElement(note_el, "lyric")
                ET.SubElement(lyric_el, "text").text = lyric_val

            current_cursor_blicks += duration_blicks

        xml_str = ET.tostring(score, encoding="utf-8", xml_declaration=True).decode("utf-8")
        os.makedirs(os.path.dirname(os.path.abspath(output_xml_path)), exist_ok=True)
        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

        print(f"✅ SVP ➡️ MusicXML 변환 완료: {output_xml_path}")
        return output_xml_path

    # =========================================================================
    # 3. Smart Lyrics Wrapper (Grouping Syllables into 2-Phrase Slides)
    # =========================================================================
    @staticmethod
    def smart_group_lyrics(tokens_with_timing: List[Dict[str, Any]], lines_per_slide: int = 2) -> List[Dict[str, Any]]:
        """
        Groups vocal syllable tokens into natural phrases and bundles them into 2-line slides.
        Uses rests/pauses (onset gap >= 1 beat) or punctuation to define phrase breaks.
        """
        valid_tokens = [
            t for t in tokens_with_timing
            if t.get("text") and t.get("text").strip() not in ("-", "", "_")
        ]

        if not valid_tokens:
            return []

        phrases: List[Dict[str, Any]] = []
        current_phrase_tokens: List[str] = []
        phrase_start_ms = valid_tokens[0].get("time_ms", 0)
        phrase_end_ms = phrase_start_ms

        for i, token in enumerate(valid_tokens):
            current_phrase_tokens.append(token["text"])
            phrase_end_ms = token.get("time_end_ms", token.get("time_ms", 0))

            # Determine whether to break phrase:
            # 1. Punctuation at end of syllable
            has_punctuation = any(token["text"].endswith(p) for p in [",", ".", "!", "?", "\n"])
            # 2. Timing gap between this note and the next note
            is_gap = False
            if i + 1 < len(valid_tokens):
                next_start = valid_tokens[i + 1].get("time_ms", 0)
                this_end = token.get("time_end_ms", 0)
                # If rest duration between syllables >= 600ms (roughly half a note)
                if next_start - this_end >= 600:
                    is_gap = True

            # 3. Syllable count threshold (e.g. 12-16 syllables per line in Korean)
            is_length_overflow = len(current_phrase_tokens) >= 14

            if has_punctuation or is_gap or is_length_overflow or (i == len(valid_tokens) - 1):
                phrase_text = " ".join("".join(current_phrase_tokens).split()).strip()
                # Clean up if it was individual syllables without spaces
                # If characters don't contain spaces, add natural spacing every word or keep as is
                phrases.append({
                    "text": phrase_text,
                    "start_ms": phrase_start_ms,
                    "end_ms": phrase_end_ms
                })
                current_phrase_tokens = []
                if i + 1 < len(valid_tokens):
                    phrase_start_ms = valid_tokens[i + 1].get("time_ms", 0)

        # Bundle phrases into slides (default: 2 phrases per slide)
        slides: List[Dict[str, Any]] = []
        slide_idx = 1
        for i in range(0, len(phrases), lines_per_slide):
            chunk = phrases[i:i + lines_per_slide]
            lines = [p["text"] for p in chunk]
            combined_text = "\n".join(lines)
            s_start = chunk[0]["start_ms"]
            s_end = chunk[-1]["end_ms"]

            slide_entry = {
                "id": f"slide_{slide_idx}",
                "title": f"Slide {slide_idx}",
                "lines": lines,
                "text": combined_text,
                "time_start_ms": int(s_start),
                "time_end_ms": int(s_end),
                # FreeShow native items compatibility
                "items": [
                    {
                        "lines": [
                            {"align": "center", "text": [{"value": line, "style": ""}]}
                            for line in lines
                        ],
                        "style": ""
                    }
                ]
            }
            slides.append(slide_entry)
            slide_idx += 1

        return slides

    # =========================================================================
    # 4. MusicXML -> FreeShow (.json)
    # =========================================================================
    def musicxml_to_freeshow(
        self,
        xml_path: str,
        output_fs_path: str,
        lines_per_slide: int = 2,
        part_id: Optional[str] = None,
        verse: int = 1
    ) -> Dict[str, Any]:
        """
        Extracts lyrics and timestamps from MusicXML (.musicxml or .mxl), formats into 2-phrase FreeShow slides.
        """
        tree, root = parse_musicxml_source(xml_path)
        part_id_found, part_name_found, target_part = get_target_part(root, part_id)

        divisions = 1
        div_el = target_part.find(".//attributes/divisions")
        if div_el is None:
            div_el = root.find(".//attributes/divisions")
        if div_el is not None and div_el.text:
            divisions = max(1, int(div_el.text.strip()))

        tempo = self.default_bpm
        sound_el = target_part.find(".//sound[@tempo]")
        if sound_el is None:
            sound_el = root.find(".//sound[@tempo]")
        if sound_el is not None and sound_el.get("tempo"):
            try:
                tempo = float(sound_el.get("tempo"))
            except ValueError:
                pass

        # Multi-staff / multi-voice handling (e.g. piano grand staff)
        staves = set(n.find('staff').text for n in target_part.findall('.//note') if n.find('staff') is not None)
        voices = set(n.find('voice').text for n in target_part.findall('.//note') if n.find('voice') is not None)
        is_multitrack = len(staves) > 1 or len(voices) > 1

        sec_per_div = (60.0 / tempo) / divisions
        current_time_sec = 0.0
        tokens_with_timing: List[Dict[str, Any]] = []

        for note in target_part.iter("note"):
            if is_multitrack:
                st = note.find("staff")
                v = note.find("voice")
                if st is not None and st.text != "1":
                    continue
                if v is not None and v.text != "1":
                    continue

            if note.find("grace") is not None:
                continue

            duration_el = note.find("duration")
            raw_duration = int(duration_el.text.strip()) if (duration_el is not None and duration_el.text) else divisions
            duration_sec = raw_duration * sec_per_div

            is_chord = note.find("chord") is not None
            note_time = current_time_sec - duration_sec if is_chord else current_time_sec

            if note.find("rest") is not None:
                if not is_chord:
                    current_time_sec += duration_sec
                continue

            lyric = extract_note_lyric(note, verse=verse)
            if lyric:
                tokens_with_timing.append({
                    "text": lyric,
                    "time_ms": int(note_time * 1000),
                    "time_end_ms": int((note_time + duration_sec) * 1000)
                })

            if not is_chord:
                current_time_sec += duration_sec

        slides = self.smart_group_lyrics(tokens_with_timing, lines_per_slide=lines_per_slide)

        fs_data = {
            "version": "1.0.0",
            "type": "show",
            "name": os.path.splitext(os.path.basename(xml_path))[0],
            "slides": slides
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_fs_path)), exist_ok=True)
        with open(output_fs_path, "w", encoding="utf-8") as f:
            json.dump(fs_data, f, indent=2, ensure_ascii=False)

        print(f"🎬 MusicXML ➡️ FreeShow 자막 변환 완료: {output_fs_path} (총 {len(slides)}개 슬라이드)")
        return fs_data

    # =========================================================================
    # 5. Synthesizer V Pro (.svp) -> FreeShow (.json)
    # =========================================================================
    def svp_to_freeshow(self, svp_path: str, output_fs_path: str, lines_per_slide: int = 2) -> Dict[str, Any]:
        """
        Extracts singing lyrics from Synthesizer V Pro (.svp), formats into FreeShow slides.
        """
        with open(svp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        tempo = 120.0
        time_info = data.get("time", {})
        if time_info.get("tempo") and len(time_info["tempo"]) > 0:
            tempo = float(time_info["tempo"][0].get("bpm", 120.0))

        sec_per_blick = (60.0 / tempo) / SV_BEAT_BLICKS

        tracks = data.get("tracks", [])
        notes: List[Dict[str, Any]] = []
        if tracks:
            track = tracks[0]
            if "mainGroup" in track and "notes" in track["mainGroup"]:
                notes = track["mainGroup"]["notes"]
            elif "notes" in track:
                notes = track["notes"]

        notes.sort(key=lambda n: n.get("onset", 0))

        tokens_with_timing: List[Dict[str, Any]] = []
        for n in notes:
            lyric = n.get("lyrics", "").strip()
            if not lyric or lyric in ("-", "_"):
                continue
            onset_blick = n.get("onset", 0)
            dur_blick = n.get("duration", 0)
            time_ms = int(onset_blick * sec_per_blick * 1000)
            time_end_ms = int((onset_blick + dur_blick) * sec_per_blick * 1000)

            tokens_with_timing.append({
                "text": lyric,
                "time_ms": time_ms,
                "time_end_ms": time_end_ms
            })

        slides = self.smart_group_lyrics(tokens_with_timing, lines_per_slide=lines_per_slide)

        fs_data = {
            "version": "1.0.0",
            "type": "show",
            "name": os.path.splitext(os.path.basename(svp_path))[0],
            "slides": slides
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_fs_path)), exist_ok=True)
        with open(output_fs_path, "w", encoding="utf-8") as f:
            json.dump(fs_data, f, indent=2, ensure_ascii=False)

        print(f"🎬 SVP ➡️ FreeShow 자막 변환 완료: {output_fs_path} (총 {len(slides)}개 슬라이드)")
        return fs_data

    # =========================================================================
    # 6. FreeShow -> MusicXML (Reverse Lyric Update)
    # =========================================================================
    def freeshow_to_musicxml(
        self,
        fs_path: str,
        template_xml_path: str,
        output_xml_path: str,
        part_id: Optional[str] = None
    ) -> str:
        """
        Reverse Update: Updates lyrics in existing MusicXML while keeping pitch, rhythm, and rests intact.
        Extracts updated lyrics from FreeShow slides and aligns them note-by-note.
        """
        # Read FreeShow
        with open(fs_path, "r", encoding="utf-8") as f:
            fs_data = json.load(f)

        slides = fs_data.get("slides", [])
        raw_text_corpus: List[str] = []

        if isinstance(slides, list):
            for s in slides:
                if "lines" in s and isinstance(s["lines"], list):
                    raw_text_corpus.extend(s["lines"])
                elif "text" in s and s["text"]:
                    raw_text_corpus.append(s["text"])
        elif isinstance(slides, dict):
            for _, s in slides.items():
                if "notes" in s and s["notes"]:
                    raw_text_corpus.append(s["notes"])

        # Tokenize text into non-whitespace Korean syllables or words
        syllables: List[str] = []
        for line in raw_text_corpus:
            for char in line:
                if not char.isspace():
                    syllables.append(char)

        if not syllables:
            print("⚠️ FreeShow에서 추출할 유효 가사 텍스트가 없습니다.")

        # Parse template MusicXML
        tree, root = parse_musicxml_source(template_xml_path)
        part_id_found, part_name_found, target_part = get_target_part(root, part_id)

        syllable_idx = 0
        updated_note_count = 0

        for note in target_part.iter("note"):
            # Skip grace notes and rests
            if note.find("grace") is not None or note.find("rest") is not None:
                continue

            # This is a singing note
            lyric_el = note.find("lyric")
            if lyric_el is None:
                lyric_el = ET.SubElement(note, "lyric")

            text_el = lyric_el.find("text")
            if text_el is None:
                text_el = ET.SubElement(lyric_el, "text")

            if syllable_idx < len(syllables):
                text_el.text = syllables[syllable_idx]
                syllable_idx += 1
                updated_note_count += 1
            else:
                text_el.text = "-"

        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        os.makedirs(os.path.dirname(os.path.abspath(output_xml_path)), exist_ok=True)
        with open(output_xml_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

        print(f"🔄 FreeShow ➡️ MusicXML 가사 역추적 업데이트 완료: {output_xml_path} (매핑된 음절: {updated_note_count}/{len(syllables)})")
        return output_xml_path

    # =========================================================================
    # 7. FreeShow -> Synthesizer V Pro (.svp)
    # =========================================================================
    def freeshow_to_svp(self, fs_path: str, template_svp_path: str, output_svp_path: str) -> str:
        """
        Reverse Update: Updates lyrics in existing SVP project while keeping melody and timings intact.
        """
        with open(fs_path, "r", encoding="utf-8") as f:
            fs_data = json.load(f)

        slides = fs_data.get("slides", [])
        raw_text_corpus: List[str] = []

        if isinstance(slides, list):
            for s in slides:
                if "lines" in s and isinstance(s["lines"], list):
                    raw_text_corpus.extend(s["lines"])
                elif "text" in s and s["text"]:
                    raw_text_corpus.append(s["text"])

        syllables: List[str] = []
        for line in raw_text_corpus:
            for char in line:
                if not char.isspace():
                    syllables.append(char)

        with open(template_svp_path, "r", encoding="utf-8") as f:
            svp_data = json.load(f)

        tracks = svp_data.get("tracks", [])
        if not tracks:
            raise ValueError("SVP 템플릿에 트랙이 존재하지 않습니다.")

        track = tracks[0]
        notes = track.get("mainGroup", {}).get("notes") or track.get("notes") or []

        syllable_idx = 0
        updated_count = 0
        for note in notes:
            if syllable_idx < len(syllables):
                note["lyrics"] = syllables[syllable_idx]
                syllable_idx += 1
                updated_count += 1
            else:
                note["lyrics"] = "-"

        os.makedirs(os.path.dirname(os.path.abspath(output_svp_path)), exist_ok=True)
        with open(output_svp_path, "w", encoding="utf-8") as f:
            json.dump(svp_data, f, indent=2, ensure_ascii=False)

        print(f"🔄 FreeShow ➡️ SVP 가사 역추적 업데이트 완료: {output_svp_path} (매핑된 음절: {updated_count}/{len(syllables)})")
        return output_svp_path

    # =========================================================================
    # 8. All-in-One 3-Way Bridge Pipeline
    # =========================================================================
    def bridge_all(
        self,
        source_path: str,
        output_dir: str,
        bpm: Optional[float] = None,
        part_id: Optional[str] = None,
        lyrics_text: Optional[str] = None,
        verse: int = 1
    ) -> Dict[str, str]:
        """
        Automated 3-Way Bridge: Takes an input file (.musicxml, .mxl, or .svp) and produces all companion files.
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        results = {}

        if source_path.endswith((".musicxml", ".xml", ".mxl")):
            svp_path = os.path.join(output_dir, f"{base_name}.svp")
            fs_path = os.path.join(output_dir, f"{base_name}_subtitles.json")

            self.musicxml_to_svp(source_path, svp_path, bpm=bpm, part_id=part_id, lyrics_text=lyrics_text, verse=verse)
            self.musicxml_to_freeshow(source_path, fs_path, part_id=part_id, verse=verse)
            results["svp"] = svp_path
            results["freeshow"] = fs_path

        elif source_path.endswith(".svp"):
            xml_path = os.path.join(output_dir, f"{base_name}.musicxml")
            fs_path = os.path.join(output_dir, f"{base_name}_subtitles.json")

            self.svp_to_musicxml(source_path, xml_path)
            self.svp_to_freeshow(source_path, fs_path)
            results["musicxml"] = xml_path
            results["freeshow"] = fs_path

        else:
            raise ValueError(f"지원하지 않는 입력 포맷입니다: {source_path}")

        print("\n🎉 3-Way 상호 연동 변환 완료!")
        for k, v in results.items():
            print(f"  - {k.upper()}: {v}")
        return results


def main():
    parser = argparse.ArgumentParser(
        description="3-Way Media Converter: MuseScore (.musicxml / .mxl) <-> Synthesizer V Pro (.svp) <-> FreeShow (.json)"
    )
    subparsers = parser.add_subparsers(dest="command", help="명령어 목록")

    # Command: xml2svp
    p_xml2svp = subparsers.add_parser("xml2svp", help="MusicXML (.musicxml / .mxl) ➡️ Synthesizer V Pro (.svp) 변환")
    p_xml2svp.add_argument("input", help="입력 .musicxml 또는 .mxl 파일 경로")
    p_xml2svp.add_argument("output", help="출력 .svp 파일 경로")
    p_xml2svp.add_argument("--bpm", type=float, default=None, help="템포 지정 (기본값: 악보 내 템포 또는 120)")
    p_xml2svp.add_argument("--part", type=str, default=None, help="다중 파트 악보 시 타겟 파트 ID 또는 이름 (예: P1, Violin 1)")
    p_xml2svp.add_argument("--verse", type=int, default=1, help="다절 악보 시 추출할 절 번호 (기본값: 1)")
    p_xml2svp.add_argument("--lyrics-file", type=str, default=None, help="외부 가사 텍스트 파일 (.txt) 경로 (악보에 가사가 없을 때 매핑)")
    p_xml2svp.add_argument("--lyrics", type=str, default=None, help="직접 입력 가사 문자열")
    p_xml2svp.add_argument("--satb", action="store_true", help="SATB 4부 합창 트랙 분리 생성")
    p_xml2svp.add_argument("--octave-guard", type=str, default=None, choices=["soprano", "alto", "tenor", "bass", "general"], help="보컬 음역대 초과 시 옥타브 자동 보정 가드")
    p_xml2svp.add_argument("--add-breath", action="store_true", help="휴지기(쉼표)에 자연스러운 호흡음(br) 자동 삽입")

    # Command: svp2xml
    p_svp2xml = subparsers.add_parser("svp2xml", help="Synthesizer V Pro (.svp) ➡️ MusicXML 변환")
    p_svp2xml.add_argument("input", help="입력 .svp 파일 경로")
    p_svp2xml.add_argument("output", help="출력 .musicxml 파일 경로")
    p_svp2xml.add_argument("--divisions", type=int, default=480, help="MusicXML divisions (기본값: 480)")

    # Command: xml2fs
    p_xml2fs = subparsers.add_parser("xml2fs", help="MusicXML (.musicxml / .mxl) ➡️ FreeShow (.json) 자막 변환")
    p_xml2fs.add_argument("input", help="입력 .musicxml 또는 .mxl 파일 경로")
    p_xml2fs.add_argument("output", help="출력 .json 파일 경로")
    p_xml2fs.add_argument("--lines-per-slide", type=int, default=2, help="슬라이드 당 구절 수 (기본값: 2)")
    p_xml2fs.add_argument("--part", type=str, default=None, help="타겟 파트 ID 또는 이름")
    p_xml2fs.add_argument("--verse", type=int, default=1, help="다절 악보 시 추출할 절 번호 (기본값: 1)")

    # Command: svp2fs
    p_svp2fs = subparsers.add_parser("svp2fs", help="Synthesizer V Pro (.svp) ➡️ FreeShow (.json) 자막 변환")
    p_svp2fs.add_argument("input", help="입력 .svp 파일 경로")
    p_svp2fs.add_argument("output", help="출력 .json 파일 경로")
    p_svp2fs.add_argument("--lines-per-slide", type=int, default=2, help="슬라이드 당 구절 수 (기본값: 2)")

    # Command: fs2xml
    p_fs2xml = subparsers.add_parser("fs2xml", help="FreeShow (.json) ➡️ MusicXML 가사 역추적 덮어쓰기")
    p_fs2xml.add_argument("input", help="수정된 FreeShow .json 파일 경로")
    p_fs2xml.add_argument("template", help="기존 원본 .musicxml 또는 .mxl 파일 경로")
    p_fs2xml.add_argument("output", help="가사가 업데이트된 출력 .musicxml 파일 경로")
    p_fs2xml.add_argument("--part", type=str, default=None, help="타겟 파트 ID 또는 이름")

    # Command: fs2svp
    p_fs2svp = subparsers.add_parser("fs2svp", help="FreeShow (.json) ➡️ Synthesizer V Pro (.svp) 가사 역추적 덮어쓰기")
    p_fs2svp.add_argument("input", help="수정된 FreeShow .json 파일 경로")
    p_fs2svp.add_argument("template", help="기존 원본 .svp 파일 경로")
    p_fs2svp.add_argument("output", help="가사가 업데이트된 출력 .svp 파일 경로")

    # Command: bridge
    p_bridge = subparsers.add_parser("bridge", help="하나의 입력 파일로 동반 포맷 동시 자동 생성")
    p_bridge.add_argument("input", help="입력 파일 (.musicxml, .mxl 또는 .svp)")
    p_bridge.add_argument("--outdir", default="./output", help="출력 디렉토리 (기본값: ./output)")
    p_bridge.add_argument("--bpm", type=float, default=None, help="템포 지정 (BPM)")
    p_bridge.add_argument("--part", type=str, default=None, help="타겟 파트 ID 또는 이름")
    p_bridge.add_argument("--verse", type=int, default=1, help="다절 악보 시 추출할 절 번호 (기본값: 1)")
    p_bridge.add_argument("--lyrics-file", type=str, default=None, help="외부 가사 텍스트 파일 경로")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    converter = MediaConverter()

    # Read lyrics file if provided
    lyrics_str = getattr(args, "lyrics", None)
    lyrics_file = getattr(args, "lyrics_file", None)
    if lyrics_file and os.path.exists(lyrics_file):
        with open(lyrics_file, "r", encoding="utf-8") as lf:
            lyrics_str = lf.read()

    verse_val = getattr(args, "verse", 1)

    try:
        if args.command == "xml2svp":
            if getattr(args, "satb", False):
                converter.musicxml_to_satb_svp(
                    args.input,
                    args.output,
                    bpm=args.bpm,
                    verse=verse_val,
                    add_breath=getattr(args, "add_breath", False),
                    lyrics_text=lyrics_str
                )
            else:
                converter.musicxml_to_svp(
                    args.input,
                    args.output,
                    bpm=args.bpm,
                    part_id=args.part,
                    lyrics_text=lyrics_str,
                    verse=verse_val,
                    vocal_role=getattr(args, "octave_guard", None),
                    add_breath=getattr(args, "add_breath", False)
                )
        elif args.command == "svp2xml":
            converter.svp_to_musicxml(args.input, args.output, divisions=args.divisions)
        elif args.command == "xml2fs":
            converter.musicxml_to_freeshow(
                args.input,
                args.output,
                lines_per_slide=args.lines_per_slide,
                part_id=args.part,
                verse=verse_val
            )
        elif args.command == "svp2fs":
            converter.svp_to_freeshow(args.input, args.output, lines_per_slide=args.lines_per_slide)
        elif args.command == "fs2xml":
            converter.freeshow_to_musicxml(args.input, args.template, args.output, part_id=args.part)
        elif args.command == "fs2svp":
            converter.freeshow_to_svp(args.input, args.template, args.output)
        elif args.command == "bridge":
            converter.bridge_all(
                args.input,
                args.outdir,
                bpm=args.bpm,
                part_id=args.part,
                lyrics_text=lyrics_str,
                verse=verse_val
            )
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
