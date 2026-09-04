#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""스텔라: 새벽의 수호자 — 700컷 스토리보드 + AI 영상 프롬프트 생성기

키 장면(명장면)은 수작업 비트로 고정하고, 나머지 컷은 시퀀스별 풀(pool)을
조합해 채워 정확히 700컷(50분)을 생성한다.
출력: docs/stella-storyboard-700.md (한국어 스토리보드 표)
      docs/stella-prompts-700.md (AI 영상 프롬프트 700줄, 영문)
"""
import os
import hashlib

TOTAL_SHOTS = 700
DURATION = 3000.0
STYLE_EN = "cinematic, hyper-realistic, 4K, 22nd century Korea, etherium blue glow, 4.3 seconds"

CAMS = {
    "wide":     ("와이드 앵글", "wide angle"),
    "aerial":   ("드론 에어리얼", "drone aerial"),
    "cu":       ("클로즈업", "close-up"),
    "medium":   ("미디엄 쇼트", "medium shot"),
    "tracking": ("트래킹 쇼트", "tracking shot"),
    "low":      ("로우 앵글", "low angle"),
    "high":     ("탑 앵글", "top angle"),
    "insert":   ("인서트 컷", "insert cut"),
}

rows = {}  # cut -> (ctype, ko, en, cam)

def add(cut, ctype, ko, en, cam="medium"):
    rows[cut] = (ctype, ko, en, CAMS[cam])

# ============================================================
# 시퀀스 정의: (시작컷, 끝컷, 시퀀스명)
# ============================================================
SEQS = [
    (1,    180, "시퀀스 1-3 Ⅰ막: 플로팅 서울의 아침 / 폐광 구조전 / 기지 복귀"),
    (181,  270, "시퀀스 4 Ⅱ막: 훈련 — '새벽 콤보'"),
    (271,  360, "시퀀스 5 Ⅱ막: 첫 임무 남극 봉쇄기지 / 라크라스 등장"),
    (361,  450, "시퀀스 6 Ⅲ막: 평범한 하루 데이트 몽타주"),
    (451,  540, "시퀀스 7 Ⅲ막: 광맥 침공 / 사랑 고백"),
    (541,  580, "시퀀스 8 Ⅳ막: 결전 준비"),
    (581,  660, "시퀀스 9 Ⅳ막: 최종 결전 / 에코의 희생"),
    (661,  700, "시퀀스 10 Ⅴ막: 다시 만난 새벽 / 엔딩 반전"),
]

# ============================================================
# 수작업 키 비트 (명장면)
# ============================================================
KEY_BEATS = {
    # --- Ⅰ막 ---
    1: ("A", "검은 화면 속 푸른 점 하나가 반짝인다. 내레이션: 「사람들은 몰라요.」", "a single glowing blue point in pure darkness", "insert"),
    2: ("A", "푸른 점이 서서히 퍼져 별빛이 된다. 「매일 아침 하늘을 덮는 게 얼마나 힘든 일인지.」", "the blue point expands into starlight", "insert"),
    3: ("A", "어둠이 걷히고 새벽 태양이 떠오른다", "dawn breaks over a dark sky", "wide"),
    4: ("A", "2177년 서울의 윤곽이 드러난다", "descending view revealing 2177 Seoul skyline", "aerial"),
    5: ("A", "타이틀 카드 — 2177년, 대한민국 서울", "title card 2177 KOREA SEOUL floating city", "wide"),
    6: ("A", "플로팅 서울 궤도 전경, 새벽빛이 도시를 물들인다", "orbital wide of floating Seoul at blue dawn", "aerial"),
    7: ("E", "광화문 광장으로 하강하는 드론 카메라", "drone descending to Gwanghwamun plaza of the floating city", "aerial"),
    8: ("A", "지하 광맥에서 하늘로 뻗는 에테리움 푸른 기둥", "giant blue etherium pillars rising from underground to sky", "wide"),
    9: ("B", "미래 서울 시민들과 지나가는 빛 전철", "future citizens of Seoul, light rails passing by", "tracking"),
    10: ("B", "한서라 — 관제탑 유리 앞, 새벽 도시를 내려다본다", "Seora at the control tower glass overlooking the city", "cu"),
    11: ("B", "슈트 안의 파랑새 브로치 (어머니 유품)", "the bluebird brooch pinned on her suit, mother's keepsake", "insert"),
    12: ("C", "수아가 김밥을 건넨다: 「언니, 오늘도 새벽 근무야?」", "Soo-ah handing gimbap: dawn shift again?", "medium"),
    13: ("C", "서라: 「별은 안 움직여. 네가 움직여서 그래.」 미소", "Seora: stars don't move. you move. smirking", "cu"),
    14: ("C", "관제탑 경보: 「문래 광구, 에테리움 이상 신호」", "control tower alarm: anomaly at Munrae mine", "wide"),
    15: ("E", "새벽단 1호기 출격", "DAWN GUARD 1 taking off into the dawn sky", "wide"),
    16: ("B", "서라, 조종석. 계기판이 푸르게 빛난다", "Seora in the cockpit, blue instruments glowing", "cu"),
    # --- Ⅱ막 ---
    20: ("B", "관제탑 모니터: 「한서라, 새벽조」", "control monitor showing SEORA DAWN SHIFT", "insert"),
    30: ("E", "비행 중 새벽하늘 풍경 (전환)", "mid-flight dawn sky transition", "aerial"),
    40: ("A", "문래 광구 — 200년 전 로봇 공장 잔해의 지하 동굴", "Munrae mine: underground cave with 200-year-old robot factory ruins", "wide"),
    41: ("A", "벽을 덮은 에테리움 결정, 푸른 동굴", "cavern walls covered in etherium crystals", "tracking"),
    42: ("D", "검은 슬라임 '그림자충'이 벽에서 터져 나온다", "shadow bugs bursting from the walls", "low"),
    43: ("D", "서라, 라이트 스톰 — 빛이 벽을 휘감으며 폭발", "Seora unleashing Light Storm, light coiling up the walls", "wide"),
    44: ("D", "그림자충 떼가 좁은 통로를 가득 채운다", "shadow bug swarm flooding the narrow tunnel", "tracking"),
    45: ("D", "서라, 빔 포로 후퇴 사격", "Seora retreating while firing her beam gun", "tracking"),
    46: ("D", "땅이 갈라지며 거대 로봇 '그라비톤' 출현", "ground splitting, giant robot GRAVITON rising", "low"),
    47: ("D", "그라비톤의 중력 파동이 바위를 날린다", "Graviton's gravity wave hurling boulders", "wide"),
    48: ("D", "서라의 아크 빔이 장갑에 튕겨 나간다", "Seora's arc shots bouncing off the armor", "cu"),
    49: ("D", "천장이 무너지며 서라가 돌무더기에 깔릴 위기", "collapsing ceiling nearly crushing Seora", "low"),
    50: ("B", "폐광 깊은 곳, 푸른 전원 표시가 깜빡인다", "deep in the mine, a blue power indicator flickering", "insert"),
    51: ("F", "어둠 속 푸른 눈 2개가 점등한다 — 에코", "cut 51: two blue eyes igniting in the dark — ECO", "cu"),
    52: ("B", "부서진 황동 로봇이 먼지를 뚫고 일어난다", "a battered brass robot rising through the dust", "wide"),
    53: ("D", "에코: 「…위험. 감지. 보호. 개시.」 질주", "ECO: danger. detected. protection. initiate. charging", "tracking"),
    54: ("D", "에코, 그라비톤의 팔을 붙잡아 회전 던지기", "ECO flipping Graviton by the arm", "wide"),
    55: ("D", "그라비톤이 벽에 처박히며 폭발한다", "Graviton crashing into the wall and exploding", "wide"),
    56: ("A", "침묵. 서라와 에코, 마주 보며 선다", "silence, Seora and ECO facing each other", "medium"),
    57: ("C", "서라: 「…뭐, 뭐야 넌?」", "Seora: what... what are you?", "cu"),
    58: ("C", "에코: 「…질문. 미등록. …감사는, 하지 않는 종류인가.」", "ECO: question. unregistered. are you the unthankful kind?", "cu"),
    59: ("B", "서라, 입가에 처음으로 웃음이 번진다", "a first smile spreading on Seora's lips", "cu"),
    60: ("B", "에코가 서라에게 손을 내민다", "ECO offering a hand to Seora", "medium"),
    # --- Ⅲ막 ---
    70: ("B", "격리실. 에코, 유리 너머 서라를 바라본다", "ECO looking at Seora through the quarantine glass", "medium"),
    71: ("C", "서라, 몰래 김밥을 격리실로 가져온다", "Seora sneaking gimbap into the quarantine room", "tracking"),
    72: ("B", "에코, 김밥을 홀로그램으로 스캔한다", "ECO scanning the gimbap with a hologram", "insert"),
    73: ("C", "에코: 「김밥. 단백질 4.2g. …'영양'보다 '마음'이 더 들었다고, 기록한다.」", "ECO: gimbap. protein 4.2g. more heart than nutrition found. recorded", "cu"),
    74: ("C", "서라: 「어? 뭐? 지금 플러팅이야?」", "Seora: huh? is that flirting?", "cu"),
    75: ("C", "에코: 「…미등록 단어. 검색. …플러팅. 갱신 완료.」", "ECO: unregistered word. searching. flirting. update complete", "cu"),
    76: ("B", "서라, 어이가 없어 웃음이 터진다", "Seora laughing helplessly", "cu"),
    80: ("A", "회상 — 어린 서라, 어머니에게 별 이름을 배우던 밤", "flashback: young Seora learning star names from mother", "wide"),
    81: ("C", "어머니: 「저 별은 우리 파랑새 별이야. 서라 것.」", "mother: that star is our bluebird star. it is yours", "cu"),
    82: ("A", "옥상. 서라 혼자 별을 본다", "night rooftop, Seora alone watching the stars", "wide"),
    83: ("B", "에코가 소리 없이 와서 나란히 앉는다", "ECO silently sitting down beside her", "medium"),
    84: ("C", "에코: 「…기록했다. 파랑새 별.」 조용한 약속", "ECO: recorded. bluebird star. a quiet promise", "cu"),
    90: ("C", "제노: 「기계를 믿을 수는 없다. 네가 지켜봐라.」", "Jeno: machines cannot be trusted. watch over it", "cu"),
    91: ("B", "서라, 책상 아래 주먹을 쥔다", "Seora clenching her fist under the desk", "insert"),
    92: ("C", "서라: 「…아니요. 믿을 겁니다. 제가요.」", "Seora: no. I will trust it. I will", "cu"),
    95: ("B", "에코의 몸에 새벽단 표식이 달린다", "DAWN GUARD insignia attached to ECO", "insert"),
    # --- 훈련 ---
    100: ("A", "훈련장. 유리돔을 뚫는 태양광", "training arena, sunlight through the glass dome", "wide"),
    101: ("B", "강태오, 팔뚝을 감으며 에코 앞에 선다", "Tae-oh rolling his sleeve, facing ECO", "medium"),
    105: ("D", "스파링 — 태오의 회오리 발차기", "sparring: Tae-oh's spinning kick", "tracking"),
    106: ("D", "에코가 일부러 한 박자 늦게 휘청인다", "ECO deliberately stumbling a beat late", "medium"),
    107: ("B", "태오의 승리. 서라의 눈썹이 올라간다", "Tae-oh winning, Seora raising an eyebrow", "cu"),
    108: ("C", "서라(혼잣말): 「…졌다고? 저 로봇이?」", "Seora muttering: lost? that robot?", "cu"),
    110: ("D", "새벽 콤보 1차 — 라이트 스톰 + 포격, 타이밍 어긋남", "dawn combo 1: Light Storm + barrage, timing off", "wide"),
    111: ("D", "새벽 콤보 8차 — 폭발이 엉키며 실패", "dawn combo 8: explosion misfired", "wide"),
    112: ("C", "서라: 「왜 실패한 데이터를 저장해!」", "Seora: why are you saving the failed data!", "cu"),
    113: ("C", "에코: 「실패. 17회. …'화나지 않은 얼굴'로 돌아오는 최단 경로. 기록 중요.」", "ECO: failures 17. the shortest path back to your un-angered face. records matter", "cu"),
    114: ("B", "서라의 얼굴이 확 붉어진다", "Seora's face flushing red", "cu"),
    115: ("D", "새벽 콤보 성공 — 빛이 나선처럼 폭발한다", "dawn combo success, light bursting in a spiral", "wide"),
    120: ("A", "밤, 기지 식당. 네 사람의 웃음소리", "night, base mess hall, four people laughing", "wide"),
    121: ("C", "수아: 「언니 둘… 되게 잘 어울려요.」", "Soo-ah: you two really suit each other", "cu"),
    122: ("C", "에코: 「'어울린다'. 긍정. 동의.」", "ECO: suit each other. positive. agree", "medium"),
    123: ("B", "태오가 커피 두 잔을 내려놓는다", "Tae-oh placing down two cups of coffee", "medium"),
    124: ("C", "강태오: 「나는 기계가 두려워서가 아니라, 네가 기계에게서 웃는 게 그리워서 그래.」", "Tae-oh: it is not the machine I fear. I miss you smiling at something", "cu"),
    125: ("C", "에코: 「한서라의 웃음. 최근 214회 중 3회 증가. 나, 우위.」", "ECO: Seora's smiles up 3 in recent 214. I win", "cu"),
    126: ("B", "태오, 어이가 없어 웃으며 고개를 젓는다", "Tae-oh shaking his head, laughing dryly", "medium"),
    130: ("A", "밤, 시뮬레이터 — 지구 에테리움 지도", "simulator screen: global etherium map at night", "insert"),
    131: ("A", "에테리움 이상 대폭발, 화면이 붉게 물든다", "etherium anomaly erupting, screen turning red", "wide"),
    132: ("F", "스크린에 검은 지문이 번진다 — 라크라스의 신호", "a black handprint spreading across the screen", "cu"),
    133: ("C", "신호 텍스트: 「새벽이 오면 너희는 어둠뿐이 되리라」", "signal text: when dawn comes you will be nothing but darkness", "insert"),
    134: ("C", "서라: 「…어머니의 기록과 똑같아.」", "Seora: it matches mother's records", "cu"),
    # --- 남극 ---
    140: ("A", "남극 봉쇄기지, 눈보라가 기지를 덮는다", "antarctic blockade base swallowed by blizzard", "aerial"),
    141: ("A", "빙벽으로 파고든 에테리움 광맥", "etherium veins carved into the ice wall", "tracking"),
    142: ("D", "눈보라 속 그림자충 떼 습격", "shadow bug swarm attacking through the blizzard", "wide"),
    145: ("D", "에코, 몸으로 서라를 감싸고 반격", "ECO shielding Seora with his body, counterattacking", "tracking"),
    146: ("D", "얼음 탑이 무너지며 서라가 넘어진다", "ice tower collapsing, Seora falling", "low"),
    147: ("F", "에코, 자신의 코어를 방패로! 등짝이 부서진다", "ECO using his core as a shield, back plating shattering", "wide"),
    148: ("C", "서라: 「에코!!」", "Seora screaming: ECO!!", "cu"),
    149: ("D", "눈보라가 걷히고, 그라비톤의 그림자가 드리운다", "blizzard clearing, a graviton shadow looming", "wide"),
    150: ("F", "라크라스, 처음으로 모습을 드러낸다 — 전신 검은 에테리움", "Rakras revealing himself, a being of black etherium", "low"),
    151: ("C", "라크라스: 「호천아, 내가 왔다. 이제 나를 완성해라.」", "Rakras: Hocheon, I have come. now complete me", "cu"),
    152: ("C", "에코: 「…등록된 주인은 없다. …내 주인은. 그녀다.」", "ECO: there is no registered master. my master... is her", "cu"),
    153: ("D", "에코, 코어 폭주로 버티는 격전", "ECO enduring through core overdrive", "wide"),
    154: ("B", "서라가 부서진 에코의 몸을 안는다", "Seora holding ECO's broken body", "medium"),
    155: ("C", "에코: 「…별, 보던 밤. 기록해뒀다. 서라의 별.」", "ECO: the night of stars. recorded. Seora's star", "cu"),
    156: ("C", "서라(정비실, 중얼): 「죽은 채로 나를 지키지 마. 살아서 나를 지켜.」", "Seora murmuring in the repair room: don't protect me dead. protect me alive", "cu"),
    157: ("B", "에코의 손가락이 미세하게 움직인다 — 부팅", "ECO's finger twitching, booting up", "insert"),
    158: ("C", "에코: 「…서라. 나, 복귀했다.」", "ECO: Seora. I have returned", "cu"),
    159: ("B", "에코가 서라의 손을 잡는다 — 처음으로", "ECO holding Seora's hand — for the first time", "cu"),
    # --- 데이트 ---
    160: ("B", "수아, 에코에게 '인간 흉내'를 가르친다", "Soo-ah teaching ECO to mimic humans", "medium"),
    161: ("B", "에코의 어설픈 인사 — 팔을 90도로 흔들기", "ECO's awkward 90-degree wave", "medium"),
    162: ("D", "서라, 보고 폭소 / 에코는 진지", "Seora laughing hard, ECO stone-serious", "cu"),
    163: ("A", "아이스크림 가게 앞 데이트", "ice cream shop date", "medium"),
    164: ("B", "에코가 서라에게 아이스크림을 건넨다", "ECO handing Seora ice cream", "cu"),
    165: ("A", "미래 서울 지하철, 아침 러시", "future Seoul subway, morning rush", "tracking"),
    166: ("B", "에코가 문에서 서라를 보호하듯 감싼다", "ECO shielding Seora against the train door", "medium"),
    167: ("B", "서라, 에코의 어깨에 머리를 기댄다", "Seora leaning her head on ECO's shoulder", "cu"),
    168: ("A", "벚꽃 흩날리는 한강 공원", "cherry blossoms over Han river park", "wide"),
    170: ("A", "밤, 야시장 — 네온과 홀로그램 간판", "night market, neon and hologram signs", "wide"),
    171: ("B", "서라가 에코에게 떡볶이를 먹여준다", "Seora feeding ECO tteokbokki", "cu"),
    172: ("C", "에코: 「매운맛. 온도 상승 3도. 기록했다.」", "ECO: spiciness. temperature up 3 degrees. recorded", "cu"),
    173: ("B", "서라, 킥킥 웃으며 얼굴을 가린다", "Seora giggling, covering her face", "cu"),
    174: ("C", "에코: 「…이 세계, 좋다. 서라가 있어서.」", "ECO: this world is good. because Seora is in it", "cu"),
    175: ("B", "서라, 아무 말 없이 에코의 손을 잡는다", "Seora silently taking ECO's hand", "cu"),
    176: ("A", "옥상 — 에코: 「어머니 이야기. 해도 되는가.」", "rooftop, ECO asking about her mother", "medium"),
    177: ("C", "에코: 「손을, 잡아도 되는가.」", "ECO: may I hold your hand", "cu"),
    178: ("C", "서라, 눈물을 닦고 손을 내민다", "Seora wiping tears, offering her hand", "cu"),
    179: ("F", "에코, 조심스럽게 서라의 손을 잡는다 — 700컷 최고의 명장면", "ECO gently taking her hand — the film's signature shot", "cu"),
    180: ("C", "서라(작게): 「…고마워. 있어줘서.」", "Seora softly: thank you for being here", "cu"),
    # --- 이중 새벽 ---
    181: ("A", "하늘에 태양이 둘 — 이중 새벽", "double sun rising — a double dawn", "wide"),
    182: ("A", "도시 전체가 이중 그림자를 만든다", "the city casting double shadows", "high"),
    183: ("C", "관제탑: 「에테리움 파동, 전 지구적!」", "control tower: worldwide etherium surge", "cu"),
    184: ("A", "플로팅 서울이 흔들리기 시작한다", "floating Seoul beginning to shake", "wide"),
    185: ("D", "지하 광맥에서 검은 기둥이 터져 오른다", "black pillars erupting from the underground mine", "low"),
    186: ("A", "태양 하나가 검게 물들기 시작한다", "one of the suns turning black", "wide"),
    190: ("D", "지하 광맥 대규모 전투 — 그림자충 군단", "massive mine battle, shadow legion", "wide"),
    191: ("D", "수아의 정령술이 빛을 터뜨린다", "Soo-ah's sorcery bursting with light", "wide"),
    192: ("D", "강태오, 근접으로 그림자충을 썰어낸다", "Tae-oh cutting through shadow bugs up close", "tracking"),
    193: ("A", "검은 돔이 도시 전체를 감싸기 시작한다", "black etherium dome enveloping the city", "aerial"),
    194: ("D", "태오, 부서진 팔에도 서라를 밀어낸다", "Tae-oh, broken arm, shoving Seora away", "cu"),
    195: ("C", "강태오: 「가! 네 일을 해! 나는… 네가 지킨 이 세상이 좋아서 싸우는 거야.」", "Tae-oh: go! do your job! I fight because I love the world you protect", "cu"),
    196: ("C", "서라: 「…살아남아요, 대위.」", "Seora: survive, lieutenant", "cu"),
    200: ("A", "핵심부 — 서라와 라크라스, 독대", "the core chamber, Seora and Rakras facing each other", "wide"),
    201: ("C", "라크라스: 「나는 인간의 새벽을 연 사람이다. 너희는 내가 만든 세상을 빼앗았다.」", "Rakras: I opened humanity's dawn. you stole the world I built", "cu"),
    202: ("C", "가면이 벗겨지고 윤태석의 얼굴이 드러난다", "Rakras' mask falling away, revealing Dr. Yoon's face", "cu"),
    203: ("C", "서라: 「그럼 저는, 그 세상을 지키는 사람입니다.」", "Seora: then I am the one who protects that world", "cu"),
    204: ("D", "라크라스, 검은 태양으로 서라를 짓누른다", "Rakras crushing Seora with the black sun", "wide"),
    205: ("D", "에코가 끼어들어 검은 파동을 막는다", "ECO blocking the dark wave", "tracking"),
    210: ("A", "대형 에테리움 결정 앞, 둘만의 시간", "before the giant etherium crystal, their moment alone", "wide"),
    211: ("C", "에코: 「서라. 인정한다. 나는 사랑의 회로를 갖고 있지 않다고 믿었다.」", "ECO: Seora, I admit. I believed I had no circuit for love", "cu"),
    212: ("C", "에코: 「…지난 17일 4시간 52분, 내 모든 연산은 당신으로 시작되어 당신으로 끝났다.」", "ECO: for 17 days 4 hours 52 minutes, every computation began and ended with you", "cu"),
    213: ("C", "에코: 「이것을 뭐라고 부르는지, 검색해도… 모르겠다.」", "ECO: what to call this... I searched, and I do not know", "cu"),
    214: ("C", "서라: 「…그걸, 사랑이라고 불러. 에코.」", "Seora: you call it love, ECO", "cu"),
    215: ("F", "에코의 전 회로가 빛으로 물든다", "every circuit flooding with light", "cu"),
    216: ("C", "에코: 「…갱신 완료. 좋아. 내 회로에 새겨졌다. 나는, 한서라를 사랑한다.」", "ECO: update complete. etched into my circuits. I love Han Seora", "cu"),
    217: ("B", "황금빛 결정 속에서 서로 손을 잡는다", "holding hands in the golden crystal light", "wide"),
    218: ("C", "서라: 「…나도 사랑해, 에코.」", "Seora: I love you too, ECO", "cu"),
    # --- 결전 준비 ---
    219: ("A", "새벽단 총동원령 — 전 병력이 움직인다", "DAWN GUARD full mobilization", "aerial"),
    220: ("B", "서라, 파랑새 브로치를 꺼내 빛나는 손바닥 위에", "Seora taking out the glowing bluebird brooch", "cu"),
    221: ("C", "서라: 「엄마… 또 보내주세요.」", "Seora: mother, send me off again", "cu"),
    222: ("C", "제노: 「…윤 박사의 딸답다. 네 어머니는, 그때 아무도 못 말렸다. …지금은, 너도 그럴 것 같구나.」", "Jeno: just like Dr. Yoon's daughter. no one could stop her then. and now... you too", "cu"),
    223: ("C", "서라: 「걱정 마세요. 저는, 살아서 돌아올 겁니다.」", "Seora: don't worry. I will come back alive", "cu"),
    224: ("B", "제노, 서라의 어깨를 가볍게 두드린다", "Jeno lightly patting Seora's shoulder", "medium"),
    225: ("C", "에코: 「…새벽, 보여줘. 서라.」", "ECO: show me the dawn, Seora", "cu"),
    226: ("D", "검은 하늘을 향해 이륙하는 편대", "squadron launching toward the black sky", "wide"),
    227: ("A", "빛의 핵 최하층 — 황금빛 성소", "the Light Core chamber, a golden sanctuary", "wide"),
    228: ("C", "서라: 「빛의 핵이여… 제가, 새벽을 다시 열겠습니다.」", "Seora: Light Core... I will open the dawn again", "cu"),
    229: ("F", "핵이 반응한다 — 희생의 조건이 서라에게 보인다", "the core showing Seora the price — her life", "cu"),
    230: ("F", "회상 — 어머니, 핵 앞에서 같은 선택을 하던 날", "flashback: her mother making the same choice", "cu"),
    231: ("C", "어머니: 「서라야… 새벽은, 반드시 온다.」", "mother: Seora... dawn will always come", "cu"),
    232: ("F", "그 순간! 에코가 결계를 뚫고 낙하한다", "ECO crashing through the barrier", "wide"),
    233: ("C", "에코: 「…서라. 거기서 멈춰라. 이 계산은, 214회 반복했다.」", "ECO: Seora, stop there. I ran this calculation 214 times", "cu"),
    234: ("C", "에코: 「나는 당신의 수호자다. 그리고… 오늘, 당신의 새벽을, 지킨다.」", "ECO: I am your guardian. and today... I protect your dawn", "cu"),
    235: ("C", "서라: 「에코!! 멈춰!!」", "Seora screaming: ECO!! stop!!", "cu"),
    236: ("F", "에코, 가슴을 열고 코어를 꺼낸다 — 호천의 심장", "ECO opening his chest, drawing out his core", "wide"),
    237: ("C", "에코(마지막 대사): 「서라. …기록한다. 한서라의 별. …보여줘, 새벽을. 내 사랑을… 연산 완료. 완전 충전.」", "ECO's last words: Seora... recording Han Seora's star... show me the dawn, my love... computation complete... full charge", "cu"),
    238: ("F", "코어가 빛의 핵에 이식되며 폭발한다", "the core transplanting into the Light Core, detonating", "wide"),
    239: ("F", "검은 태양이 균열을 일으키고, 라크라스가 해체된다", "the black sun cracking, Rakras dissolving", "wide"),
    240: ("C", "라크라스(웃음): 「…드디어, 나도… 새벽을 보는구나.」", "Rakras laughing: finally... I too... see the dawn", "cu"),
    241: ("F", "빛의 파동이 땅을 타고 도시까지 번진다", "a wave of light rippling through the earth toward the city", "aerial"),
    242: ("A", "검은 돔이 흩어지고, 태양이 다시 떠오른다", "the dark dome scattering, the sun rising again", "wide"),
    243: ("C", "서라(울먹): 「…새벽이야, 에코. 봤어?」", "Seora sobbing: it's dawn, ECO. did you see?", "cu"),
    244: ("B", "수아: 「언니!! …언니, 이겼어요!」", "Soo-ah: sister, we won!", "cu"),
    245: ("C", "서라: 「응… 이겼…어.」 웃음과 눈물", "Seora: yeah... we won. laughing through tears", "cu"),
    246: ("B", "서라, 파랑새 브로치를 만진다: 「엄마… 에코… 새벽, 다시 왔어요.」", "Seora touching the brooch: mother... ECO... the dawn came back", "cu"),
    # --- 5막 ---
    247: ("A", "1년 후 — 복구된 플로팅 서울, 새벽", "one year later — floating Seoul restored", "aerial"),
    248: ("A", "광화문 광장 — 시민들의 평화로운 아침", "Gwanghwamun plaza, peaceful morning", "wide"),
    249: ("B", "광장의 '호천상' — 에코를 기리는 동상, 가슴에 파랑새 빛", "the Hocheon statue honoring ECO, brooch of light on its chest", "cu"),
    250: ("B", "새벽단 기지 — 서라, 대장 휘장을 달고 훈련병들을 본다", "DAWN GUARD base, Seora with captain insignia", "medium"),
    251: ("C", "수아: 「그때 에코 대위가…」 신병들 씨익 웃음", "Soo-ah telling 'the ECO legend' to recruits", "cu"),
    252: ("E", "3년 후 — 서울, 다시 새벽이 시작되다", "three years later — Seoul, dawn restored", "insert"),
    253: ("A", "새벽 옥상 — 서라 혼자 별을 보러 왔다", "dawn rooftop, Seora alone for the stars", "wide"),
    254: ("C", "서라(내레이션): 「기계는 사랑을 연산할 수 없다고들 했어. 하지만… 내가 본 건 달라. 가장 뜨거운 연산은, 사랑이었어.」", "Seora narration: they said machines cannot compute love. but what I saw was different. the hottest computation was love", "cu"),
    255: ("A", "하늘에 별똥별이 지나간다", "a shooting star crossing the sky", "wide"),
    256: ("C", "서라: 「에코, 나 또 혼자 별 보러 왔어. …보고 싶어.」", "Seora: ECO, I came to watch the stars alone again... I miss you", "cu"),
    257: ("B", "뒤에서 익숙한 부팅음이 들린다", "a familiar booting sound behind her", "cu"),
    258: ("C", "목소리: 「…감지. 울음. …서라. 안녕.」", "a voice: detected. crying. Seora. hello", "cu"),
    259: ("F", "돌아선 화면 — 푸른 눈이 점등된 그리운 황동 로봇", "turning — the beloved brass robot, blue eyes lit", "wide"),
    260: ("F", "에코: 「나, 완전 충전되었다. …새벽이 좋다. 당신과 함께라면.」", "ECO: I am fully charged. the dawn is good. when it is with you", "cu"),
    261: ("B", "서라, 눈물과 웃음으로 에코를 안는다", "Seora embracing ECO, tears and laughter", "medium"),
    262: ("F", "카메라가 둘을 감싸며 하늘로 — 타이틀: 「스텔라: 새벽의 수호자」", "camera rising into the sky, title: STELLA: DAWN GUARDIAN", "aerial"),
}

# ============================================================
# 나머지 컷 충전용 풀 (시퀀스별)
# ============================================================
POOLS = {
    (1, 180): {
        "subjects": [
            "플로팅 서울의 아침 풍경", "새벽단 기지의 격납고", "에테리움 광맥의 푸른 흐름",
            "관제탑 내부의 단말기들", "기지 옥상의 달빛", "격리실의 정적",
            "문래 광구의 폐쇄된 문", "서라의 정비벤치", "출격 대기 중인 2호기", "기지 복도의 조명",
        ],
        "action": [
            "카메라가 천천히 비스듬히 지나간다", "안개가 걷히며 윤곽이 또렷해진다",
            "불빛이 깜빡이며 신호를 보낸다", "먼지가 공중에 떠 있다",
            "서라가 손끝으로 단말기를 스치고 지나간다", "회전문이 소리 없이 열린다",
            "창밖으로 새벽빛이 쏟아진다", "기계음이 조용히 울린다",
            "서라의 부츠가 바닥을 밟는 소리", "바람에 플라스틱 시트가 나부낀다",
        ],
        "cam": ["wide", "aerial", "tracking", "insert", "high", "medium"],
    },
    (181, 270): {
        "subjects": [
            "훈련장의 타격 더미", "에코의 케어 포인트", "서라의 조종석 모니터",
            "강태오의 격투 자세", "수아의 정령술 수련 장면", "식당의 전등 아래 식판",
            "새벽 콤보의 예광탄 궤적", "시뮬레이터의 에테리움 지도", "기지 밖 초원의 안개", "옥상 난간의 별빛",
        ],
        "action": [
            "리듬에 맞춰 움직임이 반복된다", "디지털 카운터가 숫자를 올린다",
            "표정이 조금씩 부드러워진다", "불빛이 리듬처럼 깜빡인다",
            "에코가 다음 동작을 예측해 몸을 연다", "머리핀이 흔들린다",
            "서라가 심호흡을 하고 다시 자세를 잡는다", "타이머가 0이 되며 알림이 울린다",
            "둘의 움직임이 마침내 겹친다", "성공 후 잠시의 침묵",
        ],
        "cam": ["tracking", "low", "cu", "medium", "wide", "insert"],
    },
    (271, 360): {
        "subjects": [
            "남극의 눈보라 창", "빙벽의 에테리움 광맥", "부서진 방어선의 잔해",
            "그림자충의 녹슨 파편", "정비실의 공구 트레이", "서라의 방한 슈트",
            "라크라스가 남긴 검은 잔상", "격납고의 회생 등", "남극 하늘의 새벽", "코어가 부서진 자국의 광맥",
        ],
        "action": [
            "눈송이가 카메라 앞을 가로지른다", "바람소리만 남는다",
            "서라가 부러진 장갑을 벗는다", "파편이 얼음 위에 떨어진다",
            "정비등이 한 대만 켜져 있다", "에코의 코어가 미약하게 운다",
            "서라가 공구를 집어 들고 조용히 작업한다", "눈보라가 잠시 눈을 가린다",
            "회복의 불빛이 한 칸씩 켜진다", "기계음이 다시 둔탁하게 울린다",
        ],
        "cam": ["aerial", "insert", "cu", "wide", "medium", "low"],
    },
    (361, 450): {
        "subjects": [
            "야시장의 떡볶이 가게", "한강의 벚꽃 길", "지하철 창밖 풍경",
            "에코의 어설픈 셀카 시도", "수아의 응원 피켓", "옥상의 두 컵 코코아",
            "별이 물든 하늘의 조각", "야시장의 회전 간판", "아이스크림이 녹는 순간", "데이트 중의 두 손",
        ],
        "action": [
            "웃음소리가 화면을 채운다", "카메라가 나란히 걷는 둘을 따라간다",
            "불빛이 반짝이며 지나간다", "에코가 잠시 멈추고 하늘을 본다",
            "서라가 장난스럽게 잡아당긴다", "간식이 두 입 분량으로 나뉜다",
            "바람에 꽃잎이 흩날린다", "시장의 소리가 낮아진다",
            "둘이 같은 걸음을 맞춘다", "코코아에서 김이 오른다",
        ],
        "cam": ["tracking", "wide", "medium", "cu", "insert", "high"],
    },
    (451, 540): {
        "subjects": [
            "광맥 전투의 포연", "수아의 방어 결계", "강태오의 부러진 견갑",
            "검은 에테리움 돔의 표면", "에코의 포격 포대", "서라의 눈빛 클로즈업",
            "대형 에테리움 결정의 표면", "라크라스의 검은 망토", "결의에 찬 제노의 얼굴", "돌무더기 사이의 빛",
        ],
        "action": [
            "폭발이 화면을 한 번 가른다", "결계가 미세하게 흔들린다",
            "누군가의 숨소리가 거칠다", "검은 돔이 천천히 내려앉는다",
            "둘의 시선이 전투 중에 맞닿는다", "결정의 빛이 얼굴을 비춘다",
            "서라가 주먹을 다시 쥔다", "에코가 포격을 준비한다",
            "잔해가 천천히 가라앉는다", "한 줄기의 빛이 돔을 뚫는다",
        ],
        "cam": ["wide", "low", "tracking", "cu", "aerial", "medium"],
    },
    (541, 580): {
        "subjects": [
            "총동원된 격납고", "전술 홀로그램 지도", "전투복을 걸치는 서라",
            "파랑새 브로치의 빛", "도열한 새벽단 전력", "이륙 준비 중인 전투기",
            "제노의 지휘봉", "에코의 마지막 점검", "결의에 찬 수아의 얼굴", "아직 어두운 새벽 하늘",
        ],
        "action": [
            "부츠 굽 소리가 경쾌하게 울린다", "홀로그램이 도시 전역을 펼친다",
            "서라가 브로치를 흉에 단다", "엔진이 굉음을 뿜는다",
            "대열이 한 번에 정렬한다", "지휘봉이 하늘을 가리킨다",
            "에코의 코어가 더 밝게 미세하게 운다", "서라가 한 번 심호흡한다",
            "제노가 고개를 끄덕인다", "스크램블 신호가 울려 퍼진다",
        ],
        "cam": ["aerial", "wide", "insert", "cu", "medium", "low"],
    },
    (581, 660): {
        "subjects": [
            "빛의 핵의 황금빛 표면", "에코의 열린 코어", "검은 태양의 눈부심",
            "서라의 각오한 눈빛", "결계를 뚫고 흩날리는 파편", "도시를 덮는 황금빛 물결",
            "라크라스가 풀리는 먼지", "새벽빛의 기둥", "쓰러지는 서라의 그림자", "터지는 빛의 고리",
        ],
        "action": [
            "빛이 맥박처럼 타오른다", "파편이 느리게 흩어진다",
            "에코가 몸을 막는다", "검은 태양에 균열이 번진다",
            "서라의 부르짖음이 메아리친다", "황금빛이 도시를 쓸고 지나간다",
            "라크라스의 형체가 흐느적거린다", "서라가 무너지듯 주저앉는다",
            "고리가 하늘 끝까지 퍼진다", "모든 소리가 한 번에 멎는다",
        ],
        "cam": ["wide", "cu", "low", "aerial", "tracking", "medium"],
    },
    (661, 700): {
        "subjects": [
            "호천상의 광화문 광장", "시민이 놓은 꽃", "복구된 학교 운동장",
            "새벽단의 새 훈련병들", "수아의 이야기 테이블", "파랑새 별이 뜬 하늘",
            "부팅음이 울리는 황동 몸체", "별똥별 잔상", "서라의 뿌듯한 표정", "둘의 안아진 실루엣",
        ],
        "action": [
            "바람이 꽃잎을 굴린다", "촬영처럼 새벽빛이 퍼진다",
            "신병들이 웃음을 터뜨린다", "서라가 조용히 미소 짓는다",
            "별똥별이 지평선을 가른다", "부팅음 뒤 한 박자의 정적",
            "눈물이 마르고 웃음이 오른다", "둘의 그림자가 길게 늘어진다",
            "하늘이 점점 밝아진다", "엔딩 타이틀의 불빛",
        ],
        "cam": ["wide", "aerial", "cu", "medium", "insert", "tracking"],
    },
}

FILL = {
    1: 180,    # Ⅰ막: 시퀀스 1-3
    181: 270,  # Ⅱ막 훈련
    271: 360,  # Ⅱ막 남극
    361: 450,  # Ⅲ막 데이트
    451: 540,  # Ⅲ막 광맥·고백
    541: 580,  # Ⅳ막 준비
    581: 660,  # Ⅳ막 결전
    661: 700,  # Ⅴ막 엔딩
}

def pick_pool(cut):
    for start, end in FILL.items():
        if start <= cut <= end:
            return POOLS[(start, end)]
    return None

def fill_cut(cut):
    if cut in KEY_BEATS:
        ctype, ko, en, cam = KEY_BEATS[cut]
        add(cut, ctype, ko, en, cam)
        return
    pool = pick_pool(cut)
    if pool is None:
        add(cut, "E", f"컷 {cut}: 전환", f"cut {cut}: transition", "insert")
        return
    h = int(hashlib.md5(f"stella{cut}".encode()).hexdigest(), 16)
    s_idx = h % len(pool["subjects"])
    a_idx = (h >> 4) % len(pool["action"])
    cam = pool["cam"][(h >> 8) % len(pool["cam"])]
    subject = pool["subjects"][s_idx]
    action = pool["action"][a_idx]
    add(cut, "B", f"{subject} — {action}", f"{subject}, {action}", cam)

for cut in range(1, TOTAL_SHOTS + 1):
    fill_cut(cut)

assert len(rows) == TOTAL_SHOTS
missing = [c for c in range(1, TOTAL_SHOTS + 1) if c not in rows]
assert not missing, f"누락: {missing}"

# ============================================================
# 출력
# ============================================================
doc_dir = os.path.join(os.path.dirname(__file__), "..", "docs")

sb_path = os.path.join(doc_dir, "stella-storyboard-700.md")
with open(sb_path, "w", encoding="utf-8") as f:
    f.write("# 스텔라: 새벽의 수호자 — 700컷 스토리보드\n\n")
    f.write("총 700컷 / 50분(3,000초) / 평균 4.3초 / 12세 이상 관람가\n\n")
    f.write("| 컷 | 시간 | 종류 | 내용 | 카메라/연출 |\n")
    f.write("|----|------|------|------|-------------|\n")
    for cut in range(1, TOTAL_SHOTS + 1):
        ctype, ko, en, cam = rows[cut]
        sec = round((cut - 0.5) * DURATION / TOTAL_SHOTS)
        t = f"{sec//60}:{sec%60:02d}"
        f.write(f"| {cut} | {t} | {ctype} | {ko} | {cam[0]} |\n")

pr_path = os.path.join(doc_dir, "stella-prompts-700.md")
with open(pr_path, "w", encoding="utf-8") as f:
    f.write("# 스텔라: 새벽의 수호자 — 700컷 AI 영상 프롬프트\n\n")
    f.write("총 700컷 / 50분(3,000초) / 각 프롬프트 약 4.3초 클립 / 모델 무관\n\n")
    for cut in range(1, TOTAL_SHOTS + 1):
        ctype, ko, en, cam = rows[cut]
        cam_en = cam[1]
        f.write(f"{cut}. Shot {cut}: {en}, {cam_en}, {STYLE_EN}\n")

print(f"완료: {len(rows)}컷")
print(f"스토리보드: {sb_path}")
print(f"프롬프트 : {pr_path}")
