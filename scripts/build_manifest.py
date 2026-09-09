import json
from pathlib import Path

# Bible Genesis 50 chapters x 2 parts = 100 episodes
chapters_info = [
    # 1
    ("천지창조 1부: 빛이 있으라! 인류 최대의 서버 오픈", "천지창조 2부: 해와 달, 그리고 인간 캐릭터 생성", "Genesis 1:1-19 Creation Days 1-3", "Genesis 1:20-31 Creation Days 4-6"),
    # 2
    ("에덴동산 1부: 신의 안식일과 파라다이스 맵 설계", "에덴동산 2부: 인류 최초의 솔로 아담과 하와 생성", "Genesis 2:1-17 Sabbath & Eden Map", "Genesis 2:18-25 Creation of Eve"),
    # 3
    ("선악과 사건 1부: 뱀의 달콤한 유혹과 금단의 열매 섭취", "선악과 사건 2부: 인류 최초 감사 청문회와 무화과 옷", "Genesis 3:1-13 Temptation of Serpent", "Genesis 3:14-24 Judgment and Expulsion"),
    # 4
    ("가인과 아벨 1부: 최초의 공물 가챠 배틀과 솔로킬", "가인과 아벨 2부: 가인의 방랑과 최초의 도시 에녹성", "Genesis 4:1-16 Cain & Abel Sacrifice", "Genesis 4:17-26 City of Enoch & Seth"),
    # 5
    ("아담의 족보 1부: 969세 므두셀라와 레전드 장수 랭킹", "아담의 족보 2부: 죽음을 보지 않고 승천한 에녹", "Genesis 5:1-20 Patriarchs Longevity", "Genesis 5:21-32 Enoch's Walk with God"),
    # 6
    ("노아의 방주 1부: 타락한 세상과 신의 대규모 리셋 선언", "노아의 방주 2부: 잣나무 방주 건조 프로젝트 착수", "Genesis 6:1-13 Corruption of Earth", "Genesis 6:14-22 Ark Construction Plan"),
    # 7
    ("대홍수 1부: 동물들 탑승 완료와 하늘의 문 개방", "대홍수 2부: 온 세상이 잠기다! 40일 밤낮의 대격변", "Genesis 7:1-16 Boarding the Ark", "Genesis 7:17-24 Catastrophic Flood"),
    # 8
    ("방주의 착륙 1부: 물이 빠지다! 까마귀와 비둘기의 정찰", "방주의 착륙 2부: 무사 하선과 노아의 첫 감사 제단", "Genesis 8:1-14 Raven and Dove Scouting", "Genesis 8:15-22 Altar of Thanksgiving"),
    # 9
    ("무지개 언약 1부: 신이 하늘에 띄운 절대 멸망 불가 표식", "무지개 언약 2부: 포도주 마신 노아의 굴욕과 아들들의 갈등", "Genesis 9:1-17 Rainbow Covenant", "Genesis 9:18-29 Noah's Vineyard"),
    # 10
    ("민족들의 계보 1부: 홍수 이후 흩어지는 세 아들의 후예", "민족들의 계보 2부: 인류 최초의 용사 니므롯의 등장", "Genesis 10:1-20 Sons of Japheth and Ham", "Genesis 10:21-32 Shem & Mighty Hunter Nimrod"),
    # 11
    ("바벨탑 사건 1부: 하늘에 닿자! 인간들의 오만한 타워 프로젝트", "바벨탑 사건 2부: 언어 뒤섞기 패치와 아브람 가문의 출발", "Genesis 11:1-9 Tower of Babel", "Genesis 11:10-32 Genealogy of Shem to Abram"),
    # 12
    ("아브라함의 부르심 1부: 본토 친척 아비 집을 떠나라!", "아브라함의 부르심 2부: 이집트 피난길과 아내 사래 구출 작전", "Genesis 12:1-9 The Call of Abram", "Genesis 12:10-20 Abram in Egypt"),
    # 13
    ("아브람과 롯 1부: 가축이 너무 많다! 목자들의 영토 갈등", "아브람과 롯 2부: 네가 좌하면 내가 우하리라! 롯의 소돔 선택", "Genesis 13:1-9 Herdsmen Quarrel", "Genesis 13:10-18 Separation & Choice of Sodom"),
    # 14
    ("소돔 연합 전쟁 1부: 4대 5 왕들의 대전쟁과 롯의 포로 위기", "소돔 연합 전쟁 2부: 야간 기습 구출과 살렘 왕 멜기세덱의 축복", "Genesis 14:1-16 Battle of Siddim & Rescue", "Genesis 14:17-24 Melchizedek Blessing"),
    # 15
    ("횃불 언약 1부: 밤하늘의 무수한 별을 보라! 자손의 약속", "횃불 언약 2부: 쪼갠 고기 사이로 지나가는 타오르는 횃불", "Genesis 15:1-8 Count the Stars", "Genesis 15:9-21 Burning Torch Covenant"),
    # 16
    ("하갈과 이스마엘 1부: 여종 하갈의 잉태와 사래의 질투", "하갈과 이스마엘 2부: 광야 샘가에서 만난 하나님과 이스마엘 출생", "Genesis 16:1-6 Hagar and Sarai Conflict", "Genesis 16:7-16 Well of Beer-lahai-roi"),
    # 17
    ("할례 언약 1부: 99세의 방문! 아브라함과 사라로 개명", "할례 언약 2부: 영원한 증표 할례와 이삭 약속에 웃음 터진 사연", "Genesis 17:1-14 Name Changes & Covenant", "Genesis 17:15-27 Abraham's Laughter & Circumcision"),
    # 18
    ("소돔의 심판 예고 1부: 상수리나무 아래 세 천사와의 만찬", "소돔의 심판 예고 2부: 50명에서 10명까지! 아브라함의 필사적 흥정", "Genesis 18:1-15 Three Angels Visit", "Genesis 18:16-33 Bargaining for Sodom"),
    # 19
    ("소돔과 고모라 1부: 도시를 덮친 유황 불벼락과 롯 일가의 탈출", "소돔과 고모라 2부: 뒤돌아보지 마라! 소금 기둥이 된 롯의 아내", "Genesis 19:1-22 Escape from Sodom", "Genesis 19:23-38 Brimstone & Pillar of Salt"),
    # 20
    ("그랄의 위기 1부: 또다시 누이라 속인 아브라함과 아비멜렉", "그랄의 위기 2부: 꿈에 나타난 경고와 아비멜렉의 사죄 보상", "Genesis 20:1-7 Abraham at Gerar", "Genesis 20:8-18 Abimelech Restores Sarah"),
    # 21
    ("이삭의 탄생 1부: 100세에 얻은 기적의 아들! 온 집안의 웃음", "이삭의 탄생 2부: 물 한 가죽부대 들고 쫓겨난 하갈과 브엘세바 우물", "Genesis 21:1-13 Birth of Isaac", "Genesis 21:14-34 Hagar in Wilderness & Beersheba"),
    # 22
    ("모리아산 번제 1부: 독자 이삭을 바치라! 인류 최대의 순종 시험", "모리아산 번제 2부: 여호와 이레! 수풀에 걸린 숫양의 기적", "Genesis 22:1-10 Sacrifice of Isaac", "Genesis 22:11-24 Jehovah-Jireh"),
    # 23
    ("사라의 죽음 1부: 127세 사라의 별세와 아브라함의 애곡", "사라의 죽음 2부: 은 400세겔로 매입한 막벨라 굴 매장지", "Genesis 23:1-9 Death of Sarah", "Genesis 23:10-20 Purchase of Machpelah Cave"),
    # 24
    ("이삭의 신붓감 찾기 1부: 종 엘리에셀의 우물가 기도와 리브가의 물동이", "이삭의 신붓감 찾기 2부: 황혼녘 들판에서의 첫 만남과 결혼 성사", "Genesis 24:1-27 Rebekah at the Well", "Genesis 24:28-67 Isaac Meets Rebekah"),
    # 25
    ("에서와 야곱 1부: 붉은 털복숭이 사냥꾼과 조용한 천막 소년", "에서와 야곱 2부: 팥죽 한 그릇에 장자권을 팔아넘긴 에서의 경솔함", "Genesis 25:1-26 Twins Born", "Genesis 25:27-34 Esau Sells Birthright for Stew"),
    # 26
    ("이삭의 우물 1부: 100배의 결실! 그랄 블레셋 사람들의 시기", "이삭의 우물 2부: 에섹, 싯나를 지나 르호봇 우물 터지다!", "Genesis 26:1-16 Hundredfold Harvest", "Genesis 26:17-35 Digging Wells at Rehoboth"),
    # 27
    ("축복 가로채기 1부: 염소 가죽 두르고 눈먼 아버지를 속인 야곱", "축복 가로채기 2부: 통곡하는 에서와 야곱의 야반도주", "Genesis 27:1-29 Deceiving Blind Isaac", "Genesis 27:30-46 Esau's Wrath & Jacob Flees"),
    # 28
    ("벧엘의 사닥다리 1부: 돌베개 베고 잠든 밤 하늘에 닿은 계단", "벧엘의 사닥다리 2부: 이곳이 하나님의 집이로다! 기둥 서원", "Genesis 28:1-15 Jacob's Ladder Dream", "Genesis 28:16-22 Bethel Pillar Vow"),
    # 29
    ("라반의 삼촌 집 1부: 우물가에서 만난 운명의 여인 라헬", "라반의 삼촌 집 2부: 첫날밤 신부 교체 사기극! 레아와 7년의 추가 노역", "Genesis 29:1-14 Jacob Meets Rachel", "Genesis 29:15-35 Laban's Wedding Switch"),
    # 30
    ("자녀들의 탄생 1부: 레아 vs 라헬의 치열한 아들 낳기 레이스", "자녀들의 탄생 2부: 얼룩무늬 양 만들기 신공! 부자 야곱의 지혜", "Genesis 30:1-24 Birth of 12 Sons", "Genesis 30:25-43 Peeled Sticks Livestock"),
    # 31
    ("라반과의 결별 1부: 낯빛이 변한 삼촌! 가족 이끌고 비밀 탈출", "라반과의 결별 2부: 추격해온 라반과 미스바 돌무더기 평화 언약", "Genesis 31:1-21 Secret Departure", "Genesis 31:22-55 Pursuit & Mizpah Covenant"),
    # 32
    ("얍복강의 씨름 1부: 400명을 거느리고 오는 에서! 야곱의 극단 공포", "얍복강의 씨름 2부: 날이 샐 때까지의 씨름! 네 이름을 이스라엘이라 하라", "Genesis 32:1-21 Fear of Esau", "Genesis 32:22-32 Wrestling at Peniel"),
    # 33
    ("형제의 눈물 화해 1부: 목을 어긋맞기며 통곡한 에서와 야곱", "형제의 눈물 화해 2부: 형님 얼굴을 보니 하나님 얼굴을 본 듯합니다", "Genesis 33:1-11 Esau and Jacob Embrace", "Genesis 33:12-20 Peace and Settling at Succoth"),
    # 34
    ("디나 사건 1부: 세겜 땅에서 일어난 수치스러운 사건", "디나 사건 2부: 시므온과 레위의 피비린내 나는 칼부림 복수극", "Genesis 34:1-17 Incident at Shechem", "Genesis 34:18-31 Vengeance of Simeon & Levi"),
    # 35
    ("벧엘로 돌아가라 1부: 우상을 묻고 정결케 하여 벧엘로 제단 쌓기", "벧엘로 돌아가라 2부: 베냐민 출산 중 숨진 라헬과 이삭의 안식", "Genesis 35:1-15 Purifying at Bethel", "Genesis 35:16-29 Birth of Benjamin & Death of Isaac"),
    # 36
    ("에서(에돔)의 족보 1부: 세일 산으로 터전을 옮긴 에서의 족보", "에서(에돔)의 족보 2부: 이스라엘 왕이 있기 전 다스린 에돔의 왕들", "Genesis 36:1-19 Line of Esau", "Genesis 36:20-43 Kings of Edom"),
    # 37
    ("요셉의 채색옷 1부: 형들의 짚단이 절하는 꿈과 채색옷 편애", "요셉의 채색옷 2부: 구덩이에 던져진 요셉! 은 20개에 팔려간 노예", "Genesis 37:1-17 Dreams of Joseph", "Genesis 37:18-36 Sold to Midianites into Egypt"),
    # 38
    ("유다와 다말 1부: 아들들의 죽음과 과부 다말의 서글픈 현실", "유다와 다말 2부: 도장과 지팡이로 밝혀진 진실! 베레스와 세라 출산", "Genesis 38:1-14 Judah's Family Tragedy", "Genesis 38:15-30 Tamar's Righteousness"),
    # 39
    ("보디발의 집 1부: 노예에서 가정 총무로! 여호와께서 함께하신 요셉", "보디발의 집 2부: 보디발 아내의 유혹 뿌리치고 억울하게 투옥되다", "Genesis 39:1-10 Prosperity in Potiphar's House", "Genesis 39:11-23 False Accusation and Prison"),
    # 40
    ("감옥 속의 꿈 해몽 1부: 술 맡은 관원장의 포도나무 세 가지 꿈", "감옥 속의 꿈 해몽 2부: 떡 굽는 관원장의 꿈과 3일 뒤의 실현", "Genesis 40:1-11 Cupbearer's Dream", "Genesis 40:12-23 Baker's Dream & Fulfillment"),
    # 41
    ("바로의 꿈과 총리 발탁 1부: 나일강의 살진 암소 일곱과 파리한 암소", "바로의 꿈과 총리 발탁 2부: 30세 죄수에서 이집트 총리로 수직 상승!", "Genesis 41:1-36 Pharaoh's Dreams", "Genesis 41:37-57 Joseph Appointed Prime Minister"),
    # 42
    ("형들의 첫 이집트 방문 1부: 쌀 사러 온 형들의 절! 20년 만의 조우", "형들의 첫 이집트 방문 2부: 스파이 의혹과 시므온 결박 투옥", "Genesis 42:1-17 Brothers Bow to Joseph", "Genesis 42:18-38 Simeon Held & Return Home"),
    # 43
    ("베냐민과 함께 2차 방문 1부: 막내를 데려오지 않으면 쌀은 없다!", "베냐민과 함께 2차 방문 2부: 총리의 저택에서 열린 눈물의 오찬 파티", "Genesis 43:1-14 Judah Guarantees Benjamin", "Genesis 43:15-34 Feast at Joseph's Palace"),
    # 44
    ("은잔 시험과 유다의 호소 1부: 베냐민 자루에서 발견된 총리의 은잔!", "은잔 시험과 유다의 호소 2부: 제가 대신 종이 되겠습니다! 유다의 탄원", "Genesis 44:1-17 Silver Cup Found", "Genesis 44:18-34 Judah's Self-Sacrifice Plea"),
    # 45
    ("요셉의 정체 공개 1부: 방성대곡하며 터져 나온 말, 내가 요셉입니다!", "요셉의 정체 공개 2부: 하나님이 생명을 구하려 나를 먼저 보내셨나이다", "Genesis 45:1-15 Joseph Weeps & Reveals Identity", "Genesis 45:16-28 Pharaoh's Wagons for Jacob"),
    # 46
    ("이집트 이주 1부: 브엘세바 밤의 이상과 70명 대가족의 이주", "이집트 이주 2부: 고센 땅에서의 극적 상봉! 아비 야곱과 아들 요셉", "Genesis 46:1-27 Vision at Beersheba & Genealogy", "Genesis 46:28-34 Reunion in Goshen"),
    # 47
    ("고센 정착과 흉년 극복 1부: 바로 앞에 선 야곱의 고백 '험악한 세월'", "고센 정착과 흉년 극복 2부: 토지 매입 정책으로 이집트를 살려낸 요셉", "Genesis 47:1-12 Jacob Meets Pharaoh", "Genesis 47:13-31 Joseph's Grain Policy & Oath"),
    # 48
    ("에브라임과 므낫세 1부: 손자들을 양자로 삼은 야곱의 임종 병상", "에브라임과 므낫세 2부: 손을 엇바꾸어 얹은 축복! 작은 자의 우선권", "Genesis 48:1-12 Jacob Adopts Grandchildren", "Genesis 48:13-22 Crossed Hands Blessing"),
    # 49
    ("야곱의 12지파 유언 1부: 유다는 사자 새끼로다! 규가 떠나지 않으리라", "야곱의 12지파 유언 2부: 담을 넘은 무성한 가지 요셉과 열두 아들 축복", "Genesis 49:1-12 Blessings of Reuben to Judah", "Genesis 49:13-33 Blessings of Joseph & Death"),
    # 50
    ("요셉의 용서와 유언 1부: 아비 야곱의 국장과 형들의 보복 공포", "요셉의 용서와 유언 2부: 당신들은 나를 해하려 했으나 하나님은 선으로 바꾸셨다", "Genesis 50:1-14 National Mourning for Jacob", "Genesis 50:15-26 Joseph's Forgiveness and Bones Oath"),
]

episodes = []
ep_num = 1

for ch_idx, (title1, title2, summary1, summary2) in enumerate(chapters_info, start=1):
    # Part 1
    slug1 = f"gen-{ch_idx:02d}-pt1"
    ep1 = {
        "episode_number": ep_num,
        "chapter": ch_idx,
        "part": 1,
        "slug": slug1,
        "title": title1,
        "biblical_reference": f"창세기 {ch_idx}장 전반부",
        "storyboard_prompt": f"A 3x3 storyboard contact sheet grid featuring biblical story of {summary1}. 9 sequential comic panels, vibrant graphic novel illustration style, sharp cinematic lines, dynamic storytelling action, consistent character designs, ancient historical setting, 9 clearly separated rectangular panels on one contact sheet.",
        "script_sections": [
            f"자, 형님들! 오늘은 창세기 {ch_idx}장 1부, 본격적인 스토리 시작합니다!",
            f"주목할 포인트! 이번 챕터는 바로 {title1.split(':')[0]}의 핵심 사건인데요!",
            f"상황이 긴박하게 돌아갑니다! 성경 역사의 분기점이 되는 결정적 순간!",
            f"여기서 등장인물의 충격적인 선택! 과연 어떤 결과가 벌어질까요?!",
            f"운영자 하나님의 놀라운 섭리와 판정이 내려지는 순간입니다!",
            f"더 흥미진진한 다음 편도 기대해주시고 구독 좋아요 부탁드립니다!"
        ],
        "voice_emotion": "열정적이고 흥미진진한 e스포츠 캐스터 중계 톤",
        "status": "planned"
    }
    episodes.append(ep1)
    ep_num += 1

    # Part 2
    slug2 = f"gen-{ch_idx:02d}-pt2"
    ep2 = {
        "episode_number": ep_num,
        "chapter": ch_idx,
        "part": 2,
        "slug": slug2,
        "title": title2,
        "biblical_reference": f"창세기 {ch_idx}장 후반부",
        "storyboard_prompt": f"A 3x3 storyboard contact sheet grid featuring biblical story of {summary2}. 9 sequential comic panels, vibrant graphic novel illustration style, sharp cinematic lines, dramatic resolution action, consistent character designs, ancient historical setting, 9 clearly separated rectangular panels on one contact sheet.",
        "script_sections": [
            f"자, 이어서 창세기 {ch_idx}장 2부! 결말을 향해 달려갑니다!",
            f"전편의 충격에 이어, 이번엔 진짜 사건의 본론으로 들어갑니다!",
            f"피할 수 없는 대면과 선택의 순간! 여기서 승패가 완전히 갈리는데요!",
            f"결국 밝혀지는 진실과 하나님의 위대한 약속이 성취되는 클라이맥스!",
            f"인간의 연약함과 하나님의 은혜가 교차하는 감동의 피날레!",
            f"다음 장에는 더 대단한 반전이 기다립니다! 다음 매치에서 뵙겠습니다!"
        ],
        "voice_emotion": "클라이맥스 샤우팅과 유쾌한 카리스마 해설 톤",
        "status": "planned"
    }
    episodes.append(ep2)
    ep_num += 1

# Mark Genesis 4 Part 1 as completed since we just built it!
for ep in episodes:
    if ep["chapter"] == 4 and ep["part"] == 1:
        ep["status"] = "completed"
        ep["project_dir"] = "projects/genesis4-cain-abel-esports"
        ep["render_path"] = "projects/genesis4-cain-abel-esports/renders/final.mp4"

manifest_data = {
    "version": "1.0",
    "series_title": "창세기 50장 100부작 e스포츠 해설 에디션 (Genesis 100 Shorts)",
    "total_episodes": 100,
    "completed_count": 1,
    "format": "9:16 vertical short-form",
    "resolution": "720x1280",
    "fps": 30,
    "methodology": "Google Flow 3x3 Grid -> slice_grid 9분할 -> VoxCPM2 음성 복제 -> Remotion 렌더링",
    "episodes": episodes
}

out_path = Path("projects/_genesis_100_series/genesis_100_manifest.json")
out_path.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2))
print(f"Generated {len(episodes)} episodes manifest at {out_path}")
