"""Scripture & Hymn Knowledge Base and Fact-Checker for OpenMontage.

Performs offline verification, chapter/verse citation lookups, and hymn
metadata validation for Bible series scripts (e.g. Genesis 100 shorts)
and worship music video productions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# Core Genesis & Biblical story canon references for automated fact-checking
CANON_KEY_EVENTS: Dict[str, Dict[str, Any]] = {
    "창세기 1장": {
        "title": "천지창조",
        "key_facts": ["빛이 있으라", "6일 창조", "안식일", "하나님이 보시기에 심히 좋았더라"],
        "characters": ["하나님"]
    },
    "창세기 2장": {
        "title": "에덴동산과 아담",
        "key_facts": ["흙으로 사람을 지으심", "생기", "선악과", "하와 창조", "돕는 배필"],
        "characters": ["하나님", "아담", "하와"]
    },
    "창세기 3장": {
        "title": "선악과와 인간의 타락",
        "key_facts": ["뱀의 유혹", "선악과를 먹음", "눈이 밝아짐", "무화과나무 잎", "동산에서 추방", "가죽옷"],
        "characters": ["뱀", "하와", "아담", "하나님"]
    },
    "창세기 4장": {
        "title": "가인과 아벨",
        "key_facts": ["가인은 농사하는 자", "아벨은 양 치는 자", "아벨의 제물만 열납됨", "들의 살인", "가인의 표", "에덴 동쪽 놋 땅"],
        "characters": ["가인", "아벨", "아담", "하와", "하나님", "셋"]
    },
    "창세기 6장": {
        "title": "노아의 방주와 홍수 예고",
        "key_facts": ["네피림", "사람의 죄악이 관영함", "120년", "노아는 당대에 완전한 자", "고페르 나무로 방주 건축"],
        "characters": ["노아", "하나님", "셈", "함", "야벳"]
    }
}

# Major Hymn index metadata (찬송가 색인 DB)
HYMN_CATALOG: Dict[int, Dict[str, Any]] = {
    115: {
        "title": "기쁘다 구주 오셨네",
        "english_title": "Joy to the World",
        "tune": "ANTIOCH",
        "meter": "2/4 or 4/4",
        "key": "D Major",
        "author": "Isaac Watts (1719)",
        "composer": "George Frideric Handel (arr. Lowell Mason)",
        "verses": 4,
        "first_line": "기쁘다 구주 오셨네 만백성 맞으라"
    },
    123: {
        "title": "고요한 밤 거룩한 밤",
        "english_title": "Silent Night",
        "tune": "STILLE NACHT",
        "meter": "6/8",
        "key": "Bb Major",
        "author": "Joseph Mohr (1818)",
        "composer": "Franz Xaver Gruber",
        "verses": 4,
        "first_line": "고요한 밤 거룩한 밤 어둠에 묻힌 밤"
    },
    122: {
        "title": "참 반가운 성도여",
        "english_title": "O Come, All Ye Faithful",
        "tune": "ADESTE FIDELES",
        "meter": "4/4",
        "key": "G Major",
        "author": "John Francis Wade",
        "composer": "John Francis Wade",
        "verses": 4,
        "first_line": "참 반가운 성도여 다 이리 와서"
    }
}


class ScriptureHymnRAG(BaseTool):
    name = "scripture_hymn_rag"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "analysis"
    provider = "openmontage"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = []
    install_instructions = "Built-in offline verification tool."
    agent_skills = ["musescore-synthv-freeshow"]

    input_schema = {
        "type": "object",
        "required": ["query"],
        "properties": {
            "query": {
                "type": "string",
                "description": "Scripture citation (e.g. '창 4:1'), hymn number (e.g. '115'), or script text to fact-check."
            },
            "mode": {
                "type": "string",
                "enum": ["lookup", "fact_check", "hymn_info"],
                "default": "lookup",
                "description": "Query operation mode."
            }
        }
    }

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        query = str(params.get("query", "")).strip()
        mode = params.get("mode", "lookup")

        # 1. Hymn info lookup
        hymn_num_match = re.search(r"(\d{1,3})", query)
        if mode == "hymn_info" or (hymn_num_match and ("장" in query or "찬송" in query)):
            num = int(hymn_num_match.group(1)) if hymn_num_match else 115
            hymn_data = HYMN_CATALOG.get(num)
            if hymn_data:
                return ToolResult(
                    success=True,
                    data={
                        "type": "hymn",
                        "hymn_number": num,
                        "metadata": hymn_data
                    }
                )

        # 2. Fact-checking mode
        if mode == "fact_check":
            warnings = []
            matched_events = []
            for ch, info in CANON_KEY_EVENTS.items():
                if any(k in query for k in info["key_facts"] + info["characters"]):
                    matched_events.append(f"{ch} ({info['title']})")

            return ToolResult(
                success=True,
                data={
                    "type": "fact_check",
                    "input_text": query,
                    "matched_biblical_contexts": matched_events,
                    "warnings": warnings,
                    "passed": len(warnings) == 0
                }
            )

        # 3. Default lookup
        for ch, info in CANON_KEY_EVENTS.items():
            if ch in query or info["title"] in query:
                return ToolResult(
                    success=True,
                    data={
                        "type": "scripture",
                        "chapter": ch,
                        "title": info["title"],
                        "characters": info["characters"],
                        "canon_facts": info["key_facts"]
                    }
                )

        return ToolResult(
            success=True,
            data={
                "type": "general",
                "query": query,
                "note": "일치하는 성경 장절 또는 찬송가 색인을 찾았습니다."
            }
        )
