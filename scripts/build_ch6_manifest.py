import json
from pathlib import Path

# Breakdown of Genesis 6 through 50 into exactly 100 episodes
sections = [
    # Gen 6 (2)
    (6, 1, "노아의 방주 1부: 인류 타락과 하나님의 대격변 리셋 선언", "The Wickedness of Earth and God's Decree"),
    (6, 2, "노아의 방주 2부: 초대형 잣나무 방주 건조 설계 착수", "Ark Blueprints and God's Covenant with Noah"),
    # Gen 7 (2)
    (7, 1, "대홍수 1부: 정결한 짐승들의 탑승과 방주 문 닫힘", "Animals Boarding the Ark and the Door Sealed"),
    (7, 2, "대홍수 2부: 하늘의 창문 개방! 온 세상을 삼킨 40일 대격변", "Catastrophic Deluge Covering High Mountains"),
    # Gen 8 (2)
    (8, 1, "방주의 착륙 1부: 물이 감하다! 까마귀와 비둘기의 비행", "Waters Receding, Raven and Dove Scouting"),
    (8, 2, "방주의 착륙 2부: 아라랏산 하선과 인류 최초의 감사 제단", "Altar of Thanksgiving and God's Promise"),
    # Gen 9 (2)
    (9, 1, "무지개 언약 1부: 하늘에 걸린 절대 멸망 불가 무지개 사인", "The Rainbow Covenant with All Living Flesh"),
    (9, 2, "무지개 언약 2부: 포도주 마신 노아의 굴욕과 아들들의 축복", "Noah's Vineyard and Sons' Destiny"),
    # Gen 10 (2)
    (10, 1, "민족들의 계보 1부: 대홍수 이후 흩어지는 노아 아들들의 가문", "Table of Nations Descendants of Noah"),
    (10, 2, "민족들의 계보 2부: 인류 최초의 사냥꾼이자 정복자 니므롯", "Mighty Hunter Nimrod and His Kingdom"),
    # Gen 11 (2)
    (11, 1, "바벨탑 사건 1부: 하늘 꼭대기까지 닿자! 오만한 타워 프로젝트", "Tower of Babel Construction"),
    (11, 2, "바벨탑 사건 2부: 언어 뒤섞기 패치와 아브람 가문의 대이동", "Language Confusion and Line of Terah to Abram"),
    # Gen 12 (2)
    (12, 1, "아브라함의 소명 1부: 본토 친척 아비 집을 떠나라! 믿음의 출발", "The Call of Abram to Leave His Country"),
    (12, 2, "아브라함의 소명 2부: 이집트 기근 피난과 아내 사래 구출 사건", "Abram in Egypt and Deliverance of Sarai"),
    # Gen 13 (2)
    (13, 1, "아브람과 롯 1부: 가축이 너무 많아 싸우는 목자들의 갈등", "Strife Between Herdsmen of Abram and Lot"),
    (13, 2, "아브람과 롯 2부: 네가 좌하면 내가 우하리라! 롯의 소돔 선택", "Abram and Lot Separate, Choice of Sodom Plain"),
    # Gen 14 (2)
    (14, 1, "소돔 연합전 1부: 4대 5 왕들의 대격돌과 롯의 포로 위기", "Battle of Siddim Valley and Lot Taken Captive"),
    (14, 2, "소돔 연합전 2부: 야간 기습 구출과 살렘 왕 멜기세덱의 십일조", "Abram's Night Rescue and Melchizedek Blessing"),
    # Gen 15 (2)
    (15, 1, "횃불 언약 1부: 밤하늘의 무수한 별을 셀 수 있나 보라", "Look at the Stars, Promise of an Heir"),
    (15, 2, "횃불 언약 2부: 쪼갠 고기 사이를 지나는 타오르는 횃불", "The Smoking Firepot and Flaming Torch Covenant"),
    # Gen 16 (2)
    (16, 1, "하갈과 이스마엘 1부: 여종 하갈의 잉태와 사래의 극심한 갈등", "Sarai and Hagar Conflict"),
    (16, 2, "하갈과 이스마엘 2부: 광야 샘가 나를 살피시는 하나님 브엘라해로이", "The Well of Beer-lahai-roi and Ishmael Born"),
    # Gen 17 (2)
    (17, 1, "할례 언약 1부: 99세의 방문! 아브라함과 사라로 이름 개명", "Name Changes to Abraham and Sarah"),
    (17, 2, "할례 언약 2부: 언약의 징표 할례와 100세 출산 약속의 웃음", "Sign of Circumcision and Promise of Isaac"),
    # Gen 18 (2)
    (18, 1, "소돔 심판 예고 1부: 상수리나무 아래 천사들에게 대접한 송아지", "Three Heavenly Visitors at Mamre"),
    (18, 2, "소돔 심판 예고 2부: 50명에서 10명까지! 소돔을 위한 필사의 중보", "Abraham's Intercession for Sodom"),
    # Gen 19 (3)
    (19, 1, "소돔의 멸망 1부: 롯의 집을 포위한 소돔 사람들의 광기", "The Angels in Sodom and the Wicked Mob"),
    (19, 2, "소돔의 멸망 2부: 하늘에서 유황 불벼락이 비같이 쏟아지다!", "Fire and Brimstone Raining on Sodom"),
    (19, 3, "소돔의 멸망 3부: 뒤돌아보지 마라! 소금 기둥이 된 롯의 아내", "Escape to Zoar and Lot's Wife Pillar of Salt"),
    # Gen 20 (2)
    (20, 1, "그랄의 위기 1부: 또다시 누이라 거짓말한 아브라함과 아비멜렉", "Abraham and King Abimelech in Gerar"),
    (20, 2, "그랄의 위기 2부: 꿈속의 경고와 모든 태를 열어주신 하나님의 기도", "Abimelech Restores Sarah with Gifts"),
    # Gen 21 (2)
    (21, 1, "이삭의 탄생 1부: 100세에 마침내 안아본 기적의 아들 이삭", "Miraculous Birth of Isaac in Old Age"),
    (21, 2, "이삭의 탄생 2부: 쫓겨난 하갈과 광야에서 터진 브엘세바 우물", "Hagar and Ishmael in Beersheba Wilderness"),
    # Gen 22 (3)
    (22, 1, "모리아산 번제 1부: 사랑하는 독자 이삭을 번제로 바치라", "God Tests Abraham: Offer Isaac as Burnt Offering"),
    (22, 2, "모리아산 번제 2부: 제단 위에 결박된 아들! 손을 멈추라", "Abraham Binds Isaac upon the Altar"),
    (22, 3, "모리아산 번제 3부: 여호와 이레! 수풀에 뿔이 걸린 숫양의 예비", "Jehovah-Jireh: The Ram Caught in the Thicket"),
    # Gen 23 (2)
    (23, 1, "사라의 별세 1부: 127세 사라의 죽음과 아브라함의 깊은 슬픔", "Death of Sarah at Kiriath-arba"),
    (23, 2, "사라의 별세 2부: 은 400세겔로 사들인 막벨라 굴 영구 매장지", "Purchase of the Field of Machpelah"),
    # Gen 24 (3)
    (24, 1, "이삭의 신붓감 1부: 종 엘리에셀의 우물가 서원 기도", "Eliezer Sent to Find a Bride for Isaac"),
    (24, 2, "이삭의 신붓감 2부: 낙타에게까지 물을 먹인 친절한 소녀 리브가", "Rebekah Draws Water for the Camels"),
    (24, 3, "이삭의 신붓감 3부: 황혼녘 들판에서의 운명적 첫 만남과 위로", "Isaac Meets Rebekah in the Evening Field"),
    # Gen 25 (2)
    (25, 1, "쌍둥이 형제 1부: 붉은 털 사냥꾼 에서와 천막에 머문 야곱", "Twins Esau and Jacob Born"),
    (25, 2, "쌍둥이 형제 2부: 붉은 팥죽 한 그릇에 장자권을 팔아넘긴 에서", "Esau Sells His Birthright for Red Stew"),
    # Gen 26 (2)
    (26, 1, "이삭의 백배 결실 1부: 흉년 중에도 백 배나 수확한 축복", "Isaac Sows in Famine and Reaps Hundredfold"),
    (26, 2, "이삭의 백배 결실 2부: 우물 양보의 미덕! 르호봇에서 터진 평화", "Digging Wells at Esek, Sitnah, and Rehoboth"),
    # Gen 27 (3)
    (27, 1, "장자의 축복 1부: 염소 가죽을 두르고 눈먼 아버지를 속인 야곱", "Jacob Disguised in Goat Skins Deceives Isaac"),
    (27, 2, "장자의 축복 2부: 야곱에게 쏟아진 하늘의 이슬과 풍성한 곡식 축복", "Isaac Pronounces the Primary Blessing on Jacob"),
    (27, 3, "장자의 축복 3부: 통곡하는 에서의 분노와 야곱의 야반도주", "Esau's Bitter Cry and Jacob Flees to Haran"),
    # Gen 28 (2)
    (28, 1, "벧엘의 사닥다리 1부: 돌베개 베고 잠든 밤 하늘에 닿은 사다리", "Jacob's Dream of the Heavenly Ladder at Bethel"),
    (28, 2, "벧엘의 사닥다리 2부: 이곳이 하나님의 집이로다! 기둥 서원", "The Pillar at Bethel and Jacob's Vow"),
    # Gen 29 (3)
    (29, 1, "외삼촌 라반의 집 1부: 우물가에서 만난 운명의 여인 라헬", "Jacob Meets Rachel at the Well of Haran"),
    (29, 2, "외삼촌 라반의 집 2부: 첫날밤 신부 교체 사기극! 레아와 7년의 눈물", "Laban's Deception: Leah Substituted for Rachel"),
    (29, 3, "외삼촌 라반의 집 3부: 라헬을 위해 다시 시작된 7년의 사랑 노역", "Jacob Serves Another Seven Years for Rachel"),
    # Gen 30 (2)
    (30, 1, "열두 아들 탄생 1부: 레아와 라헬의 치열한 아들 낳기 레이스", "The Fierce Rivalry of Wives and Birth of Sons"),
    (30, 2, "열두 아들 탄생 2부: 버드나무 껍질 신공! 얼룩무늬 양 떼의 기적", "The Peeled Rods and Jacob's Flourishing Flocks"),
    # Gen 31 (2)
    (31, 1, "라반과의 결별 1부: 외삼촌의 안색이 변했다! 야곱 일가의 비밀 탈출", "Jacob Flees Secretly from Laban"),
    (31, 2, "라반과의 결별 2부: 미스바 돌무더기 평화 언약과 평화로운 귀향", "Laban's Pursuit and the Covenant at Galeed"),
    # Gen 32 (3)
    (32, 1, "얍복강의 공포 1부: 400명의 군사를 몰고 오는 에서의 소식", "Esau Approaching with 400 Men"),
    (32, 2, "얍복강의 공포 2부: 홀로 남은 밤, 날이 샐 때까지의 천사와의 씨름", "Jacob Wrestles with the Angel at the Jabbok"),
    (32, 3, "얍복강의 공포 3부: 네 이름을 다시는 야곱이라 부르지 말라! 이스라엘", "Jacob Named Israel, Peniel The Face of God"),
    # Gen 33 (2)
    (33, 1, "형제의 눈물 상봉 1부: 일곱 번 땅에 엎드리며 다가간 야곱과 에서", "Jacob Bows Seven Times Approaching Esau"),
    (33, 2, "형제의 눈물 상봉 2부: 목을 어긋맞기며 통곡한 20년 만의 용서", "Esau Runs to Meet Jacob and Embraces Him"),
    # Gen 34 (2)
    (34, 1, "세겜 땅의 비극 1부: 야곱의 딸 디나에게 닥친 수치스러운 사건", "The Defilement of Dinah at Shechem"),
    (34, 2, "세겜 땅의 비극 2부: 시므온과 레위의 피비린내 나는 복수극", "Simeon and Levi Avenge Their Sister"),
    # Gen 35 (2)
    (35, 1, "벧엘로 올라가라 1부: 모든 이방 신상을 묻고 정결케 하여 세운 제단", "Purifying the Household and Return to Bethel"),
    (35, 2, "벧엘로 올라가라 2부: 베냐민 출산 중 숨진 라헬과 이삭의 안식", "Birth of Benjamin, Death of Rachel and Isaac"),
    # Gen 36 (2)
    (36, 1, "에돔의 족보 1부: 세일 산으로 번성해 나간 에서의 자손들", "The Descendants of Esau in Mount Seir"),
    (36, 2, "에돔의 족보 2부: 이스라엘 왕이 있기 전 다스렸던 에돔의 군주들", "The Kings Who Reigned in the Land of Edom"),
    # Gen 37 (3)
    (37, 1, "요셉의 채색옷 1부: 열한 별과 해와 달이 절하는 꿈과 채색옷 편애", "Joseph's Dreams and the Coat of Many Colors"),
    (37, 2, "요셉의 채색옷 2부: 도단 광야 구덩이에 던져진 열일곱 소년 요셉", "Brothers Plot against Joseph at Dothan"),
    (37, 3, "요셉의 채색옷 3부: 은 스무 개에 노예로 팔려간 요셉과 아버지의 통곡", "Joseph Sold into Slavery into Egypt"),
    # Gen 38 (2)
    (38, 1, "유다와 다말 1부: 아들들의 요절과 과부 다말의 서글픈 기다림", "The Sins and Tragedies in Judah's Family"),
    (38, 2, "유다와 다말 2부: 도장과 지팡이로 밝혀진 의로움! 쌍둥이 출생", "Tamar's Faithfulness and Birth of Perez"),
    # Gen 39 (2)
    (39, 1, "보디발의 집 1부: 노예에서 가정 총무로! 여호와께서 함께하신 요셉", "Joseph Blessed in the House of Potiphar"),
    (39, 2, "보디발의 집 2부: 보디발 아내의 유혹을 뿌리치고 억울하게 갇힌 감옥", "Joseph Flees Temptation and is Falsely Imprisoned"),
    # Gen 40 (2)
    (40, 1, "감옥 속 해몽 1부: 왕의 감옥에서 만난 술 관원장과 포도나무 꿈", "The Cupbearer's Dream of the Grapevine"),
    (40, 2, "감옥 속 해몽 2부: 떡 관원장의 꿈과 사흘 뒤에 닥친 엇갈린 운명", "The Baker's Dream and Exact Fulfillment"),
    # Gen 41 (3)
    (41, 1, "바로의 악몽 1부: 살진 일곱 암소와 흉측한 파리한 암소의 꿈", "Pharaoh's Troubling Dreams of Fat and Lean Cows"),
    (41, 2, "바로의 악몽 2부: 30세 죄수 요셉의 명쾌한 7년 풍년과 흉년 해몽", "Joseph Brought before Pharaoh and Interprets"),
    (41, 3, "바로의 악몽 3부: 인장 반지를 끼고 이집트 총리로 우뚝 선 요셉", "Joseph Appointed Prime Minister of All Egypt"),
    # Gen 42 (2)
    (42, 1, "형들의 이집트행 1부: 쌀 사러 온 형들의 절! 20년 만의 기적 상봉", "Brothers Bow down to Joseph Unknowingly"),
    (42, 2, "형들의 이집트행 2부: 정탐꾼 의혹과 볼모로 결박된 형 시므온", "Simeon Imprisoned and Brothers Return in Fear"),
    # Gen 43 (2)
    (43, 1, "베냐민과의 동행 1부: 막내를 데려오지 않으면 쌀은 없다! 유다의 담보", "Judah Guarantees Benjamin's Safety"),
    (43, 2, "베냐민과의 동행 2부: 총리의 궁전에서 열린 성대한 오찬 파티", "The Emotional Banquet at Joseph's Palace"),
    # Gen 44 (2)
    (44, 1, "은잔 시험 1부: 베냐민의 자루에서 발견된 총리의 보물 은잔", "The Silver Cup Discovered in Benjamin's Sack"),
    (44, 2, "은잔 시험 2부: 제가 대신 종이 되겠습니다! 유다의 눈물겨운 탄원", "Judah's Selfless Intercession for Benjamin"),
    # Gen 45 (3)
    (45, 1, "요셉의 정체 공개 1부: 방성대곡하며 털어놓은 한마디, 내가 요셉입니다!", "Joseph Breaks Down Weeping: I am Joseph!"),
    (45, 2, "요셉의 정체 공개 2부: 하나님이 생명을 구하려 나를 앞서 보내셨나이다", "God Sent Me before You to Preserve Life"),
    (45, 3, "요셉의 정체 공개 3부: 아버지를 모셔오라! 바로 왕이 내어준 호화 수레", "Pharaoh Sends Wagons to Bring Jacob"),
    # Gen 46 (2)
    (46, 1, "이집트 대이주 1부: 브엘세바 밤의 환상과 칠십 명 가문의 대이동", "God Speaks at Beersheba, Seventy Souls to Egypt"),
    (46, 2, "이집트 대이주 2부: 고센 땅에서의 눈물의 극적 상봉! 야곱과 요셉", "Jacob and Joseph Weep on Each Other's Neck"),
    # Gen 47 (2)
    (47, 1, "고센 정착과 바로 알현 1부: 바로 앞에 선 노인 야곱의 '험악한 세월'", "Jacob Blessed Pharaoh and Declares His Pilgrimage"),
    (47, 2, "고센 정착과 바로 알현 2부: 지혜로운 토지 정책으로 온 제국을 살린 요셉", "Joseph's Famine Policy Feeds All the Land"),
    # Gen 48 (2)
    (48, 1, "손자 입양과 축복 1부: 에브라임과 므낫세를 친자식으로 삼은 야곱", "Jacob Adopts Ephraim and Manasseh"),
    (48, 2, "손자 입양과 축복 2부: 손을 엇바꾸어 얹은 축복! 작은 자의 영적 우선권", "Crossed Hands Blessing over the Younger"),
    # Gen 49 (3)
    (49, 1, "야곱의 열두 지파 예언 1부: 유다는 사자 새끼로다! 왕의 홀이 떠나지 않으리라", "Prophecy for Reuben to Judah: The Scepter Shall Not Depart"),
    (49, 2, "야곱의 열두 지파 예언 2부: 담을 넘은 무성한 가지 요셉과 열두 아들 축복", "Blessings of Joseph Fruitful Bough and Brothers"),
    (49, 3, "야곱의 열두 지파 예언 3부: 막벨라 굴에 묻어달라는 유언과 조용한 임종", "Jacob's Final Charge and Peaceful Departure"),
    # Gen 50 (2)
    (50, 1, "요셉의 용서와 유언 1부: 아버지 야곱의 대규모 국장과 형들의 보복 공포", "The Mourning of Egypt and Burial at Machpelah"),
    (50, 2, "요셉의 용서와 유언 2부: 당신들은 나를 해하려 했으나 하나님은 선으로 바꾸셨다", "What You Meant for Evil, God Meant for Good")
]

episodes = []
for idx, (ch, part, title, summary) in enumerate(sections, start=1):
    slug = f"ch6-ep{idx:03d}-gen{ch:02d}-pt{part}"
    episodes.append({
        "episode_number": idx,
        "chapter": ch,
        "part": part,
        "slug": slug,
        "title": title,
        "biblical_reference": f"창세기 {ch}장 {part}부 ({summary})",
        "storyboard_prompt": f"A 3x3 storyboard contact sheet grid featuring biblical story of {summary}. 9 sequential comic panels, vibrant graphic novel illustration style, vivid cinematic colors, sharp lines, continuous epic biblical action, consistent characters, ancient setting, 9 clearly separated rectangular panels on one contact sheet.",
        "script_sections": [
            f"자, 형님들! 창세기 100부작 제{idx}화, {title.split(':')[0]} 시작합니다!",
            f"이번 에피소드는 성경 역사상 가장 위대한 사건 중 하나인데요!",
            f"주목하세요! 상황이 아주 긴박하고 스펙터클하게 흘러갑니다!",
            f"여기서 등장인물의 충격적인 결단과 믿음의 선택이 터집니다!",
            f"모든 것을 주관하시는 하나님의 놀라운 섭리가 증명되는 클라이맥스!",
            f"다음 화에는 더 소름 돋는 반전이 기다립니다! 구독과 좋아요 필수!"
        ],
        "voice_emotion": "열정적이고 박진감 넘치는 e스포츠 캐스터 중계 톤",
        "status": "planned"
    })

manifest = {
    "version": "1.0",
    "series_title": "창세기 6~50장 100부작 0크레딧 대서사 에디션 (Genesis Ch 6-50 100 Shorts)",
    "total_episodes": len(episodes),
    "completed_count": 0,
    "format": "9:16 vertical short-form",
    "resolution": "720x1280",
    "fps": 30,
    "cost_per_video_usd": 0.0,
    "methodology": "Google Flow (Nano Banana Pro / Veo 3.1 Lite) 0크레딧 -> slice_grid 9분할 -> VoxCPM2 로컬 TTS -> Remotion 9:16 렌더링",
    "episodes": episodes
}

out_dir = Path("projects/_genesis_from_ch6_series")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "genesis_ch6_100_manifest.json"
out_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"Generated {len(episodes)} episodes in {out_file}")
