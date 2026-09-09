# Format Specifications Reference: MusicXML, SVP, and FreeShow

## 1. MusicXML (Score Format)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list>
    <score-part id="P1"><part-name>Vocal</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>4</divisions>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <clef><sign>G</sign><line>2</line></clef>
      </attributes>
      <direction><sound tempo="120"/></direction>
      <note>
        <pitch>
          <step>C</step>
          <alter>0</alter>
          <octave>4</octave>
        </pitch>
        <duration>4</duration>
        <lyric><text>은</text></lyric>
      </note>
      <note><rest/><duration>4</duration></note>
    </measure>
  </part>
</score-partwise>
```

## 2. Synthesizer V Pro (.svp) (Vocal Synth Format)
- Time Base: 1 Beat = 705,600,000 blicks
- JSON Schema snippet:
```json
{
  "version": 153,
  "time": {
    "meter": [{"index": 0, "numerator": 4, "denominator": 4}],
    "tempo": [{"position": 0, "bpm": 120.0}]
  },
  "tracks": [
    {
      "name": "Track 1",
      "mainGroup": {
        "uuid": "uuid4",
        "notes": [
          {
            "musicalType": "singing",
            "onset": 0,
            "duration": 705600000,
            "lyrics": "은",
            "pitch": 60,
            "instantMode": true
          }
        ]
      },
      "mainRef": {
        "groupID": "uuid4",
        "blickAbsoluteBegin": 0,
        "blickAbsoluteEnd": -1
      }
    }
  ]
}
```

## 3. FreeShow (.json) (Presentation Subtitle Format)
- JSON Schema snippet:
```json
{
  "version": "1.0.0",
  "type": "show",
  "name": "Title",
  "slides": [
    {
      "id": "slide_1",
      "title": "Slide 1",
      "text": "은혜 아니면 나 서지 못하네\n십자가의 그 사랑 능력 아니면",
      "lines": [
        "은혜 아니면 나 서지 못하네",
        "십자가의 그 사랑 능력 아니면"
      ],
      "time_start_ms": 0,
      "time_end_ms": 8000,
      "items": [
        {
          "lines": [
            {"align": "center", "text": [{"value": "은혜 아니면 나 서지 못하네", "style": ""}]},
            {"align": "center", "text": [{"value": "십자가의 그 사랑 능력 아니면", "style": ""}]}
          ],
          "style": ""
        }
      ]
    }
  ]
}
```
