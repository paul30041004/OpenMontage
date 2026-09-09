"""Audio to MIDI & Musical Transcription Tool for OpenMontage.

Performs monophonic pitch detection and note tracking on singing vocals,
humming, or instrumental melodies using Probabilistic YIN (pYIN).
Converts audio into standard MIDI (.mid) files for Synthesizer V Pro
or MuseScore reverse-transcription workflows.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class AudioToMidiTranscriber(BaseTool):
    name = "audio_to_midi"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "audio_processing"
    provider = "librosa"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["python:librosa", "python:mido"]
    install_instructions = "Install dependencies:\n  pip install librosa mido"
    agent_skills = ["musescore-synthv-freeshow"]

    input_schema = {
        "type": "object",
        "required": ["audio_path", "output_midi_path"],
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to input singing vocal or melody audio file."
            },
            "output_midi_path": {
                "type": "string",
                "description": "Path to save the generated standard MIDI (.mid) file."
            },
            "bpm": {
                "type": "number",
                "default": 120.0,
                "description": "Tempo BPM for MIDI ticks calculation."
            },
            "min_note_duration_sec": {
                "type": "number",
                "default": 0.08,
                "description": "Minimum duration in seconds to form a note (filters noise)."
            },
            "fmin": {
                "type": "string",
                "default": "C2",
                "description": "Minimum frequency note bound (default: C2)."
            },
            "fmax": {
                "type": "string",
                "default": "C7",
                "description": "Maximum frequency note bound (default: C7)."
            }
        }
    }

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        import librosa
        import mido
        from mido import MidiFile, MidiTrack, Message, MetaMessage

        audio_path = params.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            return ToolResult(success=False, error=f"오디오 파일을 찾을 수 없습니다: {audio_path}")

        output_midi_path = params.get("output_midi_path")
        if not output_midi_path:
            return ToolResult(success=False, error="출력 MIDI 파일 경로가 지정되지 않았습니다.")

        bpm = float(params.get("bpm", 120.0))
        min_dur = float(params.get("min_note_duration_sec", 0.08))
        fmin = str(params.get("fmin", "C2"))
        fmax = str(params.get("fmax", "C7"))

        os.makedirs(os.path.dirname(os.path.abspath(output_midi_path)), exist_ok=True)

        # 1. Load Audio
        y, sr = librosa.load(audio_path, sr=22050, mono=True)

        # 2. Extract Pitch curve using Probabilistic YIN (pYIN)
        fmin_hz = librosa.note_to_hz(fmin)
        fmax_hz = librosa.note_to_hz(fmax)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y,
            fmin=fmin_hz,
            fmax=fmax_hz,
            sr=sr,
            frame_length=2048,
            hop_length=256
        )

        times = librosa.times_like(f0, sr=sr, hop_length=256)

        # 3. Segment continuous pitch frames into discrete notes
        notes: List[Dict[str, Any]] = []
        cur_pitch: Optional[int] = None
        cur_start: float = 0.0
        cur_pitches: List[float] = []

        for t, pitch_hz, is_voiced in zip(times, f0, voiced_flag):
            if is_voiced and not np.isnan(pitch_hz) and pitch_hz > 0:
                midi_val = int(round(librosa.hz_to_midi(pitch_hz)))
                if cur_pitch is None:
                    # Start of note
                    cur_pitch = midi_val
                    cur_start = t
                    cur_pitches = [pitch_hz]
                elif abs(midi_val - cur_pitch) >= 1:
                    # Pitch changed significantly -> finalize previous note
                    note_dur = t - cur_start
                    if note_dur >= min_dur:
                        notes.append({
                            "onset_sec": round(cur_start, 3),
                            "duration_sec": round(note_dur, 3),
                            "midi_pitch": cur_pitch,
                            "note_name": librosa.midi_to_note(cur_pitch)
                        })
                    cur_pitch = midi_val
                    cur_start = t
                    cur_pitches = [pitch_hz]
                else:
                    cur_pitches.append(pitch_hz)
            else:
                # Unvoiced (silence or consonant gap)
                if cur_pitch is not None:
                    note_dur = t - cur_start
                    if note_dur >= min_dur:
                        notes.append({
                            "onset_sec": round(cur_start, 3),
                            "duration_sec": round(note_dur, 3),
                            "midi_pitch": cur_pitch,
                            "note_name": librosa.midi_to_note(cur_pitch)
                        })
                    cur_pitch = None
                    cur_pitches = []

        if cur_pitch is not None:
            note_dur = times[-1] - cur_start
            if note_dur >= min_dur:
                notes.append({
                    "onset_sec": round(cur_start, 3),
                    "duration_sec": round(note_dur, 3),
                    "midi_pitch": cur_pitch,
                    "note_name": librosa.midi_to_note(cur_pitch)
                })

        # 4. Generate Standard MIDI File
        ticks_per_beat = 480
        mid = MidiFile(ticks_per_beat=ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        # Set Tempo
        tempo_microseconds = int(round(mido.bpm2tempo(bpm)))
        track.append(MetaMessage("set_tempo", tempo=tempo_microseconds, time=0))
        track.append(MetaMessage("track_name", name="Transcribed Vocal Melody", time=0))

        # Build chronological MIDI messages
        events: List[Tuple[int, str, int, int]] = []  # (tick, type, pitch, velocity)
        sec_to_ticks = (ticks_per_beat * bpm) / 60.0

        for n in notes:
            on_tick = int(round(n["onset_sec"] * sec_to_ticks))
            off_tick = int(round((n["onset_sec"] + n["duration_sec"]) * sec_to_ticks))
            p = n["midi_pitch"]
            events.append((on_tick, "note_on", p, 96))
            events.append((off_tick, "note_off", p, 0))

        # Sort events by tick
        events.sort(key=lambda x: (x[0], 0 if x[1] == "note_off" else 1))

        last_tick = 0
        for tick, ev_type, p, vel in events:
            delta = max(0, tick - last_tick)
            track.append(Message(ev_type, note=p, velocity=vel, time=delta))
            last_tick = tick

        mid.save(output_midi_path)

        return ToolResult(
            success=True,
            data={
                "output_midi_path": output_midi_path,
                "note_count": len(notes),
                "bpm": bpm,
                "first_note": notes[0] if notes else None,
                "last_note": notes[-1] if notes else None,
                "file_size": os.path.getsize(output_midi_path),
                "notes_sample": notes[:10]
            },
            artifacts=[output_midi_path]
        )
