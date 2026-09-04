"""인기 휴먼 보이스 50개 프리셋 — 인간미 가득한 일상/공감/연애/직장인 보이스.

한국 숏폼에서 가장 인기 있는 '휴먼적인 요소'가 가득한 보이스 50개.
voice_design(영어) + emotion(영어) + sample_text(한국어)로 구성.
"""

VOICE_PRESETS_HUMAN_50 = {
    # ── 1. 일상 브이로그 (5) ──────────────────────────────
    "vlog_morning": {
        "label": "아침 브이로그",
        "voice_design": "bright, fresh, cheerful Korean female, morning vlog style",
        "emotion": "bright, fresh, cheerful morning energy",
        "sample_text": "좋은 아침이에요! 오늘 하루도 힘차게 시작해볼까요?",
    },
    "vlog_daily": {
        "label": "일상 브이로그",
        "voice_design": "relaxed, natural, casual Korean female, daily vlog style",
        "emotion": "relaxed, natural, casual everyday tone",
        "sample_text": "오늘은 평범한 하루를 보냈어요. 같이 보실래요?",
    },
    "vlog_night": {
        "label": "밤 브이로그",
        "voice_design": "calm, cozy, intimate Korean female, night vlog style",
        "emotion": "calm, cozy, intimate late-night tone",
        "sample_text": "하루를 마무리하는 시간이에요. 편하게 들어주세요.",
    },
    "vlog_weekend": {
        "label": "주말 브이로그",
        "voice_design": "excited, relaxed, weekend Korean male, weekend vlog style",
        "emotion": "excited, relaxed, weekend freedom",
        "sample_text": "드디어 주말! 오늘은 뭐 하고 놀까요?",
    },
    "vlog_cafe": {
        "label": "카페 브이로그",
        "voice_design": "soft, aesthetic, cozy Korean female, cafe vlog style",
        "emotion": "soft, aesthetic, cozy cafe mood",
        "sample_text": "오늘은 조용한 카페에서 시간을 보내고 있어요.",
    },

    # ── 2. 직장인 공감 (5) ──────────────────────────────
    "office_monday": {
        "label": "월요병 직장인",
        "voice_design": "tired, relatable, office worker Korean male, monday blues style",
        "emotion": "tired, exhausted, monday blues",
        "sample_text": "월요일 아침... 다들 힘내고 있나요?",
    },
    "office_commute": {
        "label": "출근길 직장인",
        "voice_design": "rushed, busy, commuting Korean female, office commute style",
        "emotion": "rushed, busy, commuting rush",
        "sample_text": "지각이다 지각! 오늘도 뛰어갑니다!",
    },
    "office_lunch": {
        "label": "점심 고민 직장인",
        "voice_design": "indecisive, hungry, office worker Korean male, lunch dilemma style",
        "emotion": "indecisive, hungry, lunch dilemma",
        "sample_text": "오늘 점심 뭐 먹지? 이게 제일 어려운 질문이에요.",
    },
    "office_overtime": {
        "label": "야근 직장인",
        "voice_design": "exhausted, sighing, overtime Korean female, overtime style",
        "emotion": "exhausted, sighing, overtime fatigue",
        "sample_text": "오늘도 야근이네요... 다들 고생 많아요.",
    },
    "office_boss": {
        "label": "상사 공감",
        "voice_design": "frustrated, relatable, office worker Korean male, boss complaint style",
        "emotion": "frustrated, relatable, boss complaint",
        "sample_text": "우리 상사가 오늘 또... 아시죠?",
    },

    # ── 3. 학생/수험생 (5) ──────────────────────────────
    "student_exam": {
        "label": "시험기간 수험생",
        "voice_design": "stressed, desperate, student Korean female, exam period style",
        "emotion": "stressed, desperate, exam period panic",
        "sample_text": "시험 일주일 전... 아직 아무것도 안 했어요.",
    },
    "student_study": {
        "label": "공부 브이로그",
        "voice_design": "focused, determined, student Korean male, study vlog style",
        "emotion": "focused, determined, study motivation",
        "sample_text": "오늘도 도서관에서 공부 시작합니다.",
    },
    "student_school": {
        "label": "학교 일상",
        "voice_design": "cheerful, youthful, student Korean female, school life style",
        "emotion": "cheerful, youthful, school life energy",
        "sample_text": "오늘 학교에서 재밌는 일이 있었어요!",
    },
    "student_cram": {
        "label": "벼락치기",
        "voice_design": "panicked, rushed, student Korean male, cramming style",
        "emotion": "panicked, rushed, last-minute cramming",
        "sample_text": "내일 시험인데 지금부터 시작합니다. 가능할까요?",
    },
    "student_graduate": {
        "label": "취준생",
        "voice_design": "anxious, hopeful, job seeker Korean female, job hunting style",
        "emotion": "anxious, hopeful, job hunting struggle",
        "sample_text": "오늘도 서류 넣고 왔어요. 언제쯤 합격할까요?",
    },

    # ── 4. 친구 수다 (5) ──────────────────────────────
    "friend_gossip": {
        "label": "친구 수다",
        "voice_design": "chatty, gossipy, close friend Korean female, gossip style",
        "emotion": "chatty, gossipy, close friend talk",
        "sample_text": "야, 너 그거 들었어? 진짜 대박이야!",
    },
    "friend_comfort": {
        "label": "친구 위로",
        "voice_design": "caring, supportive, best friend Korean female, comfort style",
        "emotion": "caring, supportive, best friend comfort",
        "sample_text": "괜찮아, 내가 있잖아. 다 잘 될 거야.",
    },
    "friend_joke": {
        "label": "친구 장난",
        "voice_design": "playful, teasing, friend Korean male, joking style",
        "emotion": "playful, teasing, friendly joke",
        "sample_text": "야, 너 진짜 웃기다. 이거 완전 너잖아.",
    },
    "friend_advice": {
        "label": "친구 조언",
        "voice_design": "honest, blunt, close friend Korean male, advice style",
        "emotion": "honest, blunt, friend advice",
        "sample_text": "솔직하게 말할게. 이건 좀 아니야.",
    },
    "friend_reunion": {
        "label": "친구 재회",
        "voice_design": "excited, nostalgic, old friend Korean female, reunion style",
        "emotion": "excited, nostalgic, reunion joy",
        "sample_text": "오랜만이다! 너 진짜 하나도 안 변했네!",
    },

    # ── 5. 연애/썸 (5) ──────────────────────────────
    "dating_flirt": {
        "label": "썸 타는 중",
        "voice_design": "flirty, playful, romantic Korean female, flirting style",
        "emotion": "flirty, playful, romantic tension",
        "sample_text": "오늘 뭐 해? 나랑 같이 있을래?",
    },
    "dating_confession": {
        "label": "고백하는 중",
        "voice_design": "nervous, sincere, confessing Korean male, confession style",
        "emotion": "nervous, sincere, heartfelt confession",
        "sample_text": "사실 나, 너를 좋아해. 오래전부터.",
    },
    "dating_couple": {
        "label": "커플 브이로그",
        "voice_design": "sweet, affectionate, couple Korean female, couple vlog style",
        "emotion": "sweet, affectionate, couple love",
        "sample_text": "오늘은 우리 데이트하는 날이에요!",
    },
    "dating_breakup": {
        "label": "이별 후",
        "voice_design": "sad, reflective, heartbroken Korean female, breakup style",
        "emotion": "sad, reflective, heartbroken",
        "sample_text": "헤어지고 나서, 생각이 많아졌어요.",
    },
    "dating_jealous": {
        "label": "질투하는 연인",
        "voice_design": "jealous, pouty, cute Korean female, jealousy style",
        "emotion": "jealous, pouty, cute jealousy",
        "sample_text": "누구랑 그렇게 친해? 나 빼고?",
    },

    # ── 6. 가족/부모 (5) ──────────────────────────────
    "family_mom": {
        "label": "엄마 목소리",
        "voice_design": "warm, caring, motherly Korean female, mom style",
        "emotion": "warm, caring, motherly love",
        "sample_text": "밥은 먹었니? 감기 조심하고.",
    },
    "family_dad": {
        "label": "아빠 목소리",
        "voice_design": "gentle, protective, fatherly Korean male, dad style",
        "emotion": "gentle, protective, fatherly care",
        "sample_text": "힘들면 언제든 말해. 아빠가 있잖아.",
    },
    "family_grandma": {
        "label": "할머니 목소리",
        "voice_design": "warm, affectionate, grandmotherly Korean female, grandma style",
        "emotion": "warm, affectionate, grandmotherly love",
        "sample_text": "우리 손주, 많이 컸네. 밥은 먹었어?",
    },
    "family_kids": {
        "label": "아이 목소리",
        "voice_design": "cute, innocent, childlike Korean child, kids style",
        "emotion": "cute, innocent, childlike wonder",
        "sample_text": "엄마! 나 오늘 뭐 했는지 알아?",
    },
    "family_sibling": {
        "label": "형제/자매",
        "voice_design": "teasing, close, sibling Korean male, sibling style",
        "emotion": "teasing, close, sibling banter",
        "sample_text": "야, 내 거 건드리지 마. 진짜로.",
    },

    # ── 7. 자취/혼밥 (5) ──────────────────────────────
    "alone_cooking": {
        "label": "자취 요리",
        "voice_design": "proud, cozy, solo living Korean female, cooking alone style",
        "emotion": "proud, cozy, solo cooking",
        "sample_text": "오늘은 혼자서 파스타를 만들어봤어요!",
    },
    "alone_dinner": {
        "label": "혼밥",
        "voice_design": "content, peaceful, solo dining Korean male, eating alone style",
        "emotion": "content, peaceful, solo dining",
        "sample_text": "혼밥도 나름 괜찮네요. 오늘은 치킨!",
    },
    "alone_cleaning": {
        "label": "자취 청소",
        "voice_design": "satisfied, productive, solo living Korean female, cleaning style",
        "emotion": "satisfied, productive, cleaning satisfaction",
        "sample_text": "오늘은 대청소하는 날! 깨끗해지니까 기분 좋아요.",
    },
    "alone_lonely": {
        "label": "자취 외로움",
        "voice_design": "lonely, wistful, solo living Korean female, loneliness style",
        "emotion": "lonely, wistful, solo living loneliness",
        "sample_text": "혼자 있으면 가끔은 외롭기도 해요.",
    },
    "alone_freedom": {
        "label": "자취 자유",
        "voice_design": "free, happy, independent Korean male, freedom style",
        "emotion": "free, happy, independent freedom",
        "sample_text": "혼자 사니까 이게 좋아요. 완전 자유!",
    },

    # ── 8. 감성 위로 (5) ──────────────────────────────
    "comfort_hug": {
        "label": "포옹 위로",
        "voice_design": "warm, embracing, comforting Korean female, hug style",
        "emotion": "warm, embracing, comforting hug",
        "sample_text": "괜찮아요. 여기서 잠깐 쉬어가도 돼요.",
    },
    "comfort_tears": {
        "label": "눈물 위로",
        "voice_design": "gentle, tearful, empathetic Korean female, tears comfort style",
        "emotion": "gentle, tearful, empathetic comfort",
        "sample_text": "울고 싶으면 울어도 돼요. 다 이해해요.",
    },
    "comfort_encourage": {
        "label": "격려",
        "voice_design": "encouraging, uplifting, supportive Korean male, encouragement style",
        "emotion": "encouraging, uplifting, supportive",
        "sample_text": "넌 충분히 잘하고 있어. 믿어봐.",
    },
    "comfort_heal": {
        "label": "치유",
        "voice_design": "healing, peaceful, soothing Korean female, healing style",
        "emotion": "healing, peaceful, soothing",
        "sample_text": "천천히, 마음이 편안해질 때까지.",
    },
    "comfort_night": {
        "label": "밤 위로",
        "voice_design": "soft, intimate, late-night Korean female, night comfort style",
        "emotion": "soft, intimate, late-night comfort",
        "sample_text": "잠들기 전에, 오늘도 수고했다고 말해주고 싶어요.",
    },

    # ── 9. 자학 개그 (5) ──────────────────────────────
    "selfdeprecating_money": {
        "label": "돈 없는 자학",
        "voice_design": "self-deprecating, humorous, broke Korean male, money joke style",
        "emotion": "self-deprecating, humorous, broke joke",
        "sample_text": "통장 잔고를 봤는데... 웃음만 나오네요.",
    },
    "selfdeprecating_diet": {
        "label": "다이어트 자학",
        "voice_design": "self-deprecating, funny, dieting Korean female, diet joke style",
        "emotion": "self-deprecating, funny, diet failure joke",
        "sample_text": "오늘부터 다이어트... 내일부터요.",
    },
    "selfdeprecating_single": {
        "label": "솔로 자학",
        "voice_design": "self-deprecating, witty, single Korean male, single joke style",
        "emotion": "self-deprecating, witty, single joke",
        "sample_text": "올해도 솔로 크리스마스네요. 익숙해요.",
    },
    "selfdeprecating_age": {
        "label": "나이 자학",
        "voice_design": "self-deprecating, humorous, aging Korean female, age joke style",
        "emotion": "self-deprecating, humorous, age joke",
        "sample_text": "체력이 예전 같지 않네요. 나이 들었나 봐요.",
    },
    "selfdeprecating_lazy": {
        "label": "게으름 자학",
        "voice_design": "self-deprecating, lazy, humorous Korean male, laziness joke style",
        "emotion": "self-deprecating, lazy, humorous",
        "sample_text": "오늘 할 일? 내일로 미뤘습니다.",
    },

    # ── 10. MZ 세대 (5) ──────────────────────────────
    "mz_trend": {
        "label": "MZ 트렌드",
        "voice_design": "trendy, hip, gen-z Korean female, mz trend style",
        "emotion": "trendy, hip, gen-z energy",
        "sample_text": "이거 요즘 완전 핫하잖아요! 다들 알죠?",
    },
    "mz_slang": {
        "label": "MZ 신조어",
        "voice_design": "playful, slangy, gen-z Korean male, slang style",
        "emotion": "playful, slangy, gen-z slang",
        "sample_text": "이거 완전 꿀잼이에요. 인정?",
    },
    "mz_reaction": {
        "label": "MZ 리액션",
        "voice_design": "exaggerated, reactive, gen-z Korean female, reaction style",
        "emotion": "exaggerated, reactive, gen-z reaction",
        "sample_text": "와... 이건 진짜 미쳤다. 소름 돋았어요.",
    },
    "mz_opinion": {
        "label": "MZ 의견",
        "voice_design": "confident, opinionated, gen-z Korean male, opinion style",
        "emotion": "confident, opinionated, gen-z opinion",
        "sample_text": "제 생각에는 이게 맞다고 봐요. 반박 환영.",
    },
    "mz_lifestyle": {
        "label": "MZ 라이프스타일",
        "voice_design": "stylish, modern, gen-z Korean female, lifestyle style",
        "emotion": "stylish, modern, gen-z lifestyle",
        "sample_text": "요즘 제 라이프스타일, 보여드릴게요.",
    },
}
