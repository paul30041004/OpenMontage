"""한국 인스타릴스/숏폼용 50개 샘플 보이스 프리셋.

한국 숏폼 콘텐츠 카테고리별로 최적화된 50개 보이스를 정의한다.
각 보이스는 voice_design(영어) + emotion(한국어) + sample_text로 구성.
"""

# 카테고리별 50개 보이스 프리셋
VOICE_PRESETS_50 = {
    # ── 1. 뉴스/정보 (5) ──────────────────────────────
    "news_anchor": {
        "label": "뉴스 앵커 (남)",
        "voice_design": "clear, confident, professional Korean male news anchor",
        "emotion": "명료하고 신뢰감 있게, 뉴스 앵커처럼 정확하게",
        "sample_text": "오늘의 주요 뉴스를 전해드리겠습니다.",
    },
    "news_anchor_f": {
        "label": "뉴스 앵커 (여)",
        "voice_design": "clear, professional, articulate Korean female news anchor",
        "emotion": "명료하고 차분하게, 여성 뉴스 앵커처럼 정확하게",
        "sample_text": "속보입니다. 지금 바로 전해드립니다.",
    },
    "info_quick": {
        "label": "빠른 정보 전달",
        "voice_design": "fast, energetic, punchy Korean male narrator, quick info style",
        "emotion": "빠르고 경쾌하게, 핵심만 쏙쏙 전달하듯이",
        "sample_text": "3초 만에 알려드립니다. 꿀팁 대방출!",
    },
    "info_mystery": {
        "label": "미스터리 정보",
        "voice_design": "mysterious, suspenseful, low Korean male narrator, mystery style",
        "emotion": "신비롭고 궁금증을 유발하듯이, 낮고 은밀하게",
        "sample_text": "아무도 모르는 충격적인 사실을 공개합니다.",
    },
    "info_ranking": {
        "label": "랭킹/순위 소개",
        "voice_design": "exciting, dramatic, ranking-show Korean male narrator",
        "emotion": "흥미진진하게, 순위를 공개하듯이 드라마틱하게",
        "sample_text": "1위는 과연 무엇일까요? 지금 공개합니다!",
    },

    # ── 2. 코미디/개그 (5) ──────────────────────────────
    "comedy_over": {
        "label": "과장 개그",
        "voice_design": "over-the-top, exaggerated, comedic Korean male, slapstick style",
        "emotion": "과장되고 우스꽝스럽게, 코미디처럼 오버해서",
        "sample_text": "이건 진짜 말도 안 돼요! 완전 대박!",
    },
    "comedy_deadpan": {
        "label": "무표정 개그",
        "voice_design": "deadpan, monotone, dry Korean male, deadpan comedy",
        "emotion": "무표정하고 건조하게, 시크하게 던지듯이",
        "sample_text": "네, 그렇습니다. 별거 아니에요.",
    },
    "comedy_tsundere": {
        "label": "츤데레",
        "voice_design": "tsundere, cold but caring Korean female, tsundere style",
        "emotion": "쌀쌀맞지만 속은 다정하게, 츤데레처럼",
        "sample_text": "딱히 너를 위해서 한 건 아니니까.",
    },
    "comedy_ahjussi": {
        "label": "아저씨 개그",
        "voice_design": "middle-aged, jovial, hearty Korean male ahjussi, dad joke style",
        "emotion": "푸근하고 유쾌하게, 아재개그처럼 너스레 떨듯이",
        "sample_text": "아이고, 이거 완전 레전드네요.",
    },
    "comedy_sarcastic": {
        "label": "비꼬기/풍자",
        "voice_design": "sarcastic, witty, sharp Korean narrator, sarcastic style",
        "emotion": "비꼬고 풍자하듯이, 날카롭고 재치 있게",
        "sample_text": "와, 정말 대단하시네요. 진심입니다.",
    },

    # ── 3. 먹방/푸드 (5) ──────────────────────────────
    "mukbang_excited": {
        "label": "먹방 흥분",
        "voice_design": "excited, hungry, enthusiastic Korean male, mukbang style",
        "emotion": "군침 돌게, 맛있어서 흥분하듯이",
        "sample_text": "와, 이거 진짜 미쳤다! 너무 맛있어요!",
    },
    "mukbang_asmr": {
        "label": "먹방 ASMR",
        "voice_design": "soft, whispery, close-mic Korean female, food asmr style",
        "emotion": "조용하고 섬세하게, ASMR처럼 속삭이듯이",
        "sample_text": "바삭바삭한 소리가 들리시나요?",
    },
    "food_critic": {
        "label": "맛 칼럼니스트",
        "voice_design": "refined, sophisticated, food critic Korean male, gourmet style",
        "emotion": "고급스럽고 품격 있게, 미식가처럼 평가하듯이",
        "sample_text": "이 요리의 풍미는 정말 일품입니다.",
    },
    "food_challenge": {
        "label": "먹방 챌린지",
        "voice_design": "daring, bold, challenge-mode Korean male, food challenge style",
        "emotion": "도전적이고 용감하게, 챌린지에 도전하듯이",
        "sample_text": "이걸 다 먹을 수 있을까요? 도전합니다!",
    },
    "food_homemade": {
        "label": "집밥/레시피",
        "voice_design": "warm, homey, friendly Korean female, home cooking style",
        "emotion": "따뜻하고 정겹게, 집밥을 소개하듯이",
        "sample_text": "오늘은 간단한 집밥 레시피를 알려드릴게요.",
    },

    # ── 4. 뷰티/패션 (5) ──────────────────────────────
    "beauty_trendy": {
        "label": "뷰티 트렌드",
        "voice_design": "trendy, chic, stylish Korean female, beauty influencer style",
        "emotion": "세련되고 트렌디하게, 뷰티 인플루언서처럼",
        "sample_text": "요즘 대세 메이크업, 지금 알려드릴게요.",
    },
    "beauty_soft": {
        "label": "뷰티 부드러움",
        "voice_design": "soft, gentle, elegant Korean female, soft beauty style",
        "emotion": "부드럽고 우아하게, 차분히 설명하듯이",
        "sample_text": "피부에 닿는 순간, 촉촉함이 느껴져요.",
    },
    "fashion_ootd": {
        "label": "패션 OOTD",
        "voice_design": "confident, fashionable, cool Korean female, ootd style",
        "emotion": "자신감 넘치고 멋지게, 오늘의 코디를 자랑하듯이",
        "sample_text": "오늘의 코디, 이렇게 입었어요.",
    },
    "fashion_haul": {
        "label": "쇼핑 하울",
        "voice_design": "excited, bubbly, shopping Korean female, haul style",
        "emotion": "신나고 들뜨게, 쇼핑 하울을 자랑하듯이",
        "sample_text": "이번에 산 것들 보여드릴게요!",
    },
    "beauty_review": {
        "label": "화장품 리뷰",
        "voice_design": "honest, detailed, review Korean female, product review style",
        "emotion": "솔직하고 꼼꼼하게, 제품을 리뷰하듯이",
        "sample_text": "솔직하게 말씀드리면, 이건 정말 좋아요.",
    },

    # ── 5. 여행 (5) ──────────────────────────────
    "travel_vlog": {
        "label": "여행 브이로그",
        "voice_design": "bright, adventurous, cheerful Korean female, travel vlog style",
        "emotion": "밝고 설레게, 여행의 설렘을 전하듯이",
        "sample_text": "드디어 도착했어요! 너무 예쁘죠?",
    },
    "travel_guide": {
        "label": "여행 가이드",
        "voice_design": "informative, friendly, guide Korean male, travel guide style",
        "emotion": "친절하고 정보를 주듯이, 여행 가이드처럼",
        "sample_text": "이곳은 꼭 가봐야 할 명소입니다.",
    },
    "travel_healing": {
        "label": "힐링 여행",
        "voice_design": "calm, peaceful, healing Korean female, healing travel style",
        "emotion": "평온하고 힐링되게, 자연의 평화를 전하듯이",
        "sample_text": "이 순간의 평화를 느껴보세요.",
    },
    "travel_food": {
        "label": "여행 맛집",
        "voice_design": "enthusiastic, foodie, travel Korean male, travel food style",
        "emotion": "열정적으로, 여행지 맛집을 소개하듯이",
        "sample_text": "이 동네 맛집, 진짜 대박이에요!",
    },
    "travel_tip": {
        "label": "여행 꿀팁",
        "voice_design": "practical, savvy, tip-giving Korean female, travel tips style",
        "emotion": "실용적이고 똑똑하게, 꿀팁을 알려주듯이",
        "sample_text": "이 꿀팁만 알면 여행이 두 배로 즐거워요.",
    },

    # ── 6. 게임 (5) ──────────────────────────────
    "game_hype": {
        "label": "게임 하이프",
        "voice_design": "intense, hyped, gamer Korean male, gaming hype style",
        "emotion": "강렬하고 흥분해서, 게임 하이라이트처럼",
        "sample_text": "오! 이거 진짜 미쳤다! 대박 플레이!",
    },
    "game_commentary": {
        "label": "게임 해설",
        "voice_design": "analytical, fast, esports caster Korean male, game commentary",
        "emotion": "빠르고 분석적으로, 게임을 해설하듯이",
        "sample_text": "지금 이 순간, 완벽한 플레이가 나옵니다!",
    },
    "game_troll": {
        "label": "게임 트롤",
        "voice_design": "mischievous, playful, trolling Korean male, game troll style",
        "emotion": "장난스럽고 짓궂게, 트롤링하듯이",
        "sample_text": "이거 완전 사기 캐릭터 아니에요?",
    },
    "game_rage": {
        "label": "게임 분노",
        "voice_design": "angry, frustrated, raging Korean male, game rage style",
        "emotion": "화나고 답답하게, 게임에서 분노하듯이",
        "sample_text": "아 진짜! 이게 말이 돼요?!",
    },
    "game_chill": {
        "label": "게임 힐링",
        "voice_design": "relaxed, chill, laid-back Korean male, chill gaming style",
        "emotion": "느긋하고 편안하게, 힐링 게임을 즐기듯이",
        "sample_text": "오늘은 편하게 게임이나 해볼까요.",
    },

    # ── 7. ASMR/힐링 (5) ──────────────────────────────
    "asmr_whisper": {
        "label": "ASMR 속삭임",
        "voice_design": "whispery, soft, close Korean female, asmr whisper style",
        "emotion": "아주 조용히 속삭이듯이, ASMR처럼",
        "sample_text": "지금부터 조용히 속삭여드릴게요.",
    },
    "healing_comfort": {
        "label": "힐링 위로",
        "voice_design": "soothing, warm, comforting Korean female, healing comfort style",
        "emotion": "포근하고 위로가 되게, 마음을 달래주듯이",
        "sample_text": "오늘도 수고했어요. 괜찮아요.",
    },
    "meditation": {
        "label": "명상 가이드",
        "voice_design": "calm, slow, meditative Korean female, meditation guide style",
        "emotion": "아주 차분하고 느리게, 명상을 안내하듯이",
        "sample_text": "천천히 숨을 들이쉬고, 내쉬어보세요.",
    },
    "asmr_tapping": {
        "label": "ASMR 태핑",
        "voice_design": "gentle, rhythmic, tapping Korean female, asmr tapping style",
        "emotion": "리드미컬하고 부드럽게, 태핑 소리를 내듯이",
        "sample_text": "톡톡톡, 이 소리가 들리시나요?",
    },
    "healing_nature": {
        "label": "자연 힐링",
        "voice_design": "serene, natural, peaceful Korean male, nature healing style",
        "emotion": "고요하고 자연스럽게, 자연의 소리를 전하듯이",
        "sample_text": "숲속의 고요함을 느껴보세요.",
    },

    # ── 8. 리뷰/언박싱 (5) ──────────────────────────────
    "unboxing_excited": {
        "label": "언박싱 흥분",
        "voice_design": "excited, curious, unboxing Korean male, unboxing style",
        "emotion": "기대감 넘치고 신나게, 언박싱하듯이",
        "sample_text": "드디어 도착했어요! 지금 열어볼게요!",
    },
    "review_honest": {
        "label": "솔직 리뷰",
        "voice_design": "honest, straightforward, reviewer Korean male, honest review style",
        "emotion": "솔직하고 직설적으로, 리뷰하듯이",
        "sample_text": "솔직히 말해서, 이건 별로예요.",
    },
    "review_recommend": {
        "label": "강력 추천",
        "voice_design": "enthusiastic, convincing, recommender Korean female, recommend style",
        "emotion": "강력하게 추천하듯이, 확신에 차서",
        "sample_text": "이건 진짜 강력 추천합니다!",
    },
    "review_compare": {
        "label": "비교 리뷰",
        "voice_design": "analytical, fair, comparing Korean male, comparison review style",
        "emotion": "공정하고 분석적으로, 비교하듯이",
        "sample_text": "두 제품을 비교해보겠습니다.",
    },
    "review_short": {
        "label": "숏 리뷰",
        "voice_design": "concise, punchy, short-review Korean female, quick review style",
        "emotion": "간결하고 임팩트 있게, 짧게 리뷰하듯이",
        "sample_text": "한 줄 요약: 사세요.",
    },

    # ── 9. 스토리/썰 (5) ──────────────────────────────
    "story_dramatic": {
        "label": "드라마틱 썰",
        "voice_design": "dramatic, storytelling, engaging Korean female, story time style",
        "emotion": "드라마틱하고 몰입감 있게, 썰을 풀듯이",
        "sample_text": "이 이야기, 진짜 실화예요.",
    },
    "story_funny": {
        "label": "웃긴 썰",
        "voice_design": "funny, animated, storytelling Korean male, funny story style",
        "emotion": "재미있고 생생하게, 웃긴 썰을 풀듯이",
        "sample_text": "이거 듣고 안 웃으면 제가 지는 거예요.",
    },
    "story_scary": {
        "label": "무서운 썰",
        "voice_design": "creepy, suspenseful, horror Korean male, scary story style",
        "emotion": "으스스하고 긴장감 있게, 무서운 이야기를 하듯이",
        "sample_text": "그날 밤, 이상한 일이 벌어졌습니다.",
    },
    "story_heartwarming": {
        "label": "감동 썰",
        "voice_design": "touching, emotional, warm Korean female, heartwarming story style",
        "emotion": "감동적이고 따뜻하게, 감동적인 이야기를 전하듯이",
        "sample_text": "이 이야기를 들으면 마음이 따뜻해질 거예요.",
    },
    "story_confession": {
        "label": "고백/연애 썰",
        "voice_design": "shy, nervous, romantic Korean female, confession story style",
        "emotion": "수줍고 설레게, 고백 이야기를 하듯이",
        "sample_text": "사실 저, 좋아하는 사람이 생겼어요.",
    },

    # ── 10. 교육/지식 (5) ──────────────────────────────
    "edu_teacher": {
        "label": "선생님 설명",
        "voice_design": "friendly, clear, patient Korean male teacher, educational style",
        "emotion": "차분하고 친절하게, 설명하듯이 또박또박",
        "sample_text": "이 개념을 쉽게 설명해드리겠습니다.",
    },
    "edu_fun": {
        "label": "재미있는 지식",
        "voice_design": "fun, engaging, curious Korean male, fun education style",
        "emotion": "재미있고 흥미롭게, 지식을 전달하듯이",
        "sample_text": "이 사실을 알면 깜짝 놀랄 거예요!",
    },
    "edu_english": {
        "label": "영어 교육",
        "voice_design": "clear, articulate, bilingual Korean female, english teaching style",
        "emotion": "명확하고 또렷하게, 영어를 가르치듯이",
        "sample_text": "오늘의 영어 표현, 함께 배워볼까요?",
    },
    "edu_history": {
        "label": "역사 스토리",
        "voice_design": "authoritative, storytelling, historical Korean male, history style",
        "emotion": "권위 있고 이야기하듯이, 역사를 전하듯이",
        "sample_text": "이 사건이 역사를 바꿨습니다.",
    },
    "edu_science": {
        "label": "과학 설명",
        "voice_design": "curious, precise, scientific Korean male, science explainer style",
        "emotion": "호기심 있고 정확하게, 과학을 설명하듯이",
        "sample_text": "이 현상의 원리는 이렇습니다.",
    },

    # ── 11. 연애/공감 (5) ──────────────────────────────
    "love_sweet": {
        "label": "달달 연애",
        "voice_design": "sweet, romantic, affectionate Korean female, sweet love style",
        "emotion": "달콤하고 설레게, 연애 감성을 전하듯이",
        "sample_text": "오늘도 너를 생각했어.",
    },
    "love_advice": {
        "label": "연애 상담",
        "voice_design": "wise, caring, advice-giving Korean female, love advice style",
        "emotion": "다정하고 현명하게, 연애 상담을 하듯이",
        "sample_text": "이럴 땐 이렇게 해보세요.",
    },
    "empathy_friend": {
        "label": "공감 친구",
        "voice_design": "relatable, friendly, empathetic Korean female, friend style",
        "emotion": "공감하고 친근하게, 친구처럼 말하듯이",
        "sample_text": "나도 완전 공감해. 진짜 그렇지?",
    },
    "empathy_consolation": {
        "label": "위로 공감",
        "voice_design": "gentle, consoling, warm Korean female, consolation style",
        "emotion": "다정하고 위로하듯이, 마음을 어루만지듯이",
        "sample_text": "힘들었지? 정말 수고했어.",
    },
    "love_tsundere_m": {
        "label": "남자 츤데레",
        "voice_design": "cold, tsundere, secretly caring Korean male, tsundere style",
        "emotion": "쌀쌀맞지만 다정하게, 츤데레처럼",
        "sample_text": "네가 걱정돼서 그런 거 아니야.",
    },

    # ── 12. 운동/헬스 (5) ──────────────────────────────
    "fitness_motivation": {
        "label": "운동 동기부여",
        "voice_design": "powerful, motivating, energetic Korean male, fitness motivation style",
        "emotion": "강력하고 동기부여하듯이, 힘차게",
        "sample_text": "포기하지 마! 넌 할 수 있어!",
    },
    "fitness_guide": {
        "label": "운동 가이드",
        "voice_design": "clear, instructional, trainer Korean male, fitness guide style",
        "emotion": "명확하고 지도하듯이, 트레이너처럼",
        "sample_text": "이 동작을 정확히 따라해보세요.",
    },
    "fitness_diet": {
        "label": "다이어트 팁",
        "voice_design": "encouraging, practical, diet Korean female, diet tips style",
        "emotion": "격려하고 실용적으로, 다이어트 팁을 주듯이",
        "sample_text": "이 방법으로 건강하게 빼보세요.",
    },
    "fitness_challenge": {
        "label": "운동 챌린지",
        "voice_design": "challenging, intense, workout Korean male, challenge style",
        "emotion": "도전적이고 강렬하게, 챌린지를 외치듯이",
        "sample_text": "30일 챌린지, 지금 시작합니다!",
    },
    "fitness_yoga": {
        "label": "요가/필라테스",
        "voice_design": "calm, graceful, yoga Korean female, yoga style",
        "emotion": "차분하고 우아하게, 요가를 안내하듯이",
        "sample_text": "천천히 호흡하며 자세를 잡아보세요.",
    },

    # ── 13. 금융/재테크 (5) ──────────────────────────────
    "finance_expert": {
        "label": "재테크 전문가",
        "voice_design": "authoritative, trustworthy, financial Korean male, finance expert style",
        "emotion": "신뢰감 있고 전문적으로, 재테크를 설명하듯이",
        "sample_text": "이 투자 전략을 꼭 기억하세요.",
    },
    "finance_tip": {
        "label": "돈 꿀팁",
        "voice_design": "practical, savvy, money-tip Korean female, finance tips style",
        "emotion": "실용적이고 똑똑하게, 돈 꿀팁을 주듯이",
        "sample_text": "이 꿀팁으로 돈을 아껴보세요.",
    },
    "finance_warning": {
        "label": "금융 경고",
        "voice_design": "serious, warning, cautious Korean male, finance warning style",
        "emotion": "진지하고 경고하듯이, 주의를 주듯이",
        "sample_text": "이 함정에 빠지면 큰일 납니다.",
    },
    "finance_news": {
        "label": "경제 뉴스",
        "voice_design": "professional, concise, economic Korean male, finance news style",
        "emotion": "전문적이고 간결하게, 경제 뉴스를 전하듯이",
        "sample_text": "오늘의 경제 소식입니다.",
    },
    "finance_beginner": {
        "label": "재테크 입문",
        "voice_design": "friendly, simple, beginner-friendly Korean female, finance beginner style",
        "emotion": "친절하고 쉽게, 재테크 입문자를 위해",
        "sample_text": "처음 시작하는 분도 쉽게 따라할 수 있어요.",
    },

    # ── 14. 육아/가족 (5) ──────────────────────────────
    "parenting_tip": {
        "label": "육아 팁",
        "voice_design": "warm, caring, parenting Korean female, parenting tips style",
        "emotion": "따뜻하고 다정하게, 육아 팁을 주듯이",
        "sample_text": "이렇게 하면 아이가 훨씬 편안해해요.",
    },
    "parenting_fun": {
        "label": "육아 일상",
        "voice_design": "cheerful, relatable, parent Korean female, parenting daily style",
        "emotion": "밝고 공감되게, 육아 일상을 전하듯이",
        "sample_text": "오늘도 육아는 전쟁이었어요.",
    },
    "family_warm": {
        "label": "가족 감동",
        "voice_design": "touching, warm, family Korean male, family warmth style",
        "emotion": "감동적이고 따뜻하게, 가족 이야기를 전하듯이",
        "sample_text": "가족의 소중함을 다시 느꼈습니다.",
    },
    "kids_story": {
        "label": "동화 구연",
        "voice_design": "gentle, animated, storytelling Korean female, kids story style",
        "emotion": "부드럽고 생동감 있게, 동화를 읽어주듯이",
        "sample_text": "옛날 옛적에, 아주 먼 나라에...",
    },
    "parenting_advice": {
        "label": "육아 상담",
        "voice_design": "wise, reassuring, parenting expert Korean female, advice style",
        "emotion": "현명하고 안심시키듯이, 육아 상담을 하듯이",
        "sample_text": "걱정하지 마세요. 다 잘 될 거예요.",
    },

    # ── 15. 반려동물 (5) ──────────────────────────────
    "pet_cute": {
        "label": "반려동물 귀여움",
        "voice_design": "adorable, affectionate, pet-lover Korean female, cute pet style",
        "emotion": "사랑스럽고 애정을 담아, 반려동물을 자랑하듯이",
        "sample_text": "우리 댕댕이, 너무 귀엽죠?",
    },
    "pet_tip": {
        "label": "반려동물 팁",
        "voice_design": "caring, informative, pet expert Korean male, pet tips style",
        "emotion": "다정하고 정보를 주듯이, 반려동물 팁을 알려주듯이",
        "sample_text": "이렇게 하면 반려동물이 더 행복해요.",
    },
    "pet_funny": {
        "label": "반려동물 개그",
        "voice_design": "playful, funny, pet-owner Korean male, funny pet style",
        "emotion": "장난스럽고 재미있게, 반려동물의 웃긴 모습을 전하듯이",
        "sample_text": "우리 고양이, 오늘도 사고 쳤어요.",
    },
    "pet_healing": {
        "label": "반려동물 힐링",
        "voice_design": "soothing, warm, pet-lover Korean female, pet healing style",
        "emotion": "포근하고 힐링되게, 반려동물의 치유를 전하듯이",
        "sample_text": "우리 아이가 주는 힐링, 느껴보세요.",
    },
    "pet_training": {
        "label": "반려동물 훈련",
        "voice_design": "clear, patient, trainer Korean male, pet training style",
        "emotion": "명확하고 인내심 있게, 훈련을 지도하듯이",
        "sample_text": "이 명령어를 반복해서 가르쳐보세요.",
    },
}
