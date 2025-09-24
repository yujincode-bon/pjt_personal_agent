# nodes/combination_node.py

from state import AgentState

# ✅ 좋은/나쁜 조합 정의 (향후 DB/JSON으로 확장 가능)
GOOD_COMBOS = [
    ("Vitamin C", "Iron"),
    ("Vitamin D", "Calcium"),
    ("Magnesium", "Vitamin B6")
]

BAD_COMBOS = [
    ("Calcium", "Iron"),
    ("Zinc", "Magnesium"),
    ("Iron", "Coffee")
]

def combination_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current = profile.get("current_intake", [])
    recommendations = state.get("recommendations", [])

    # ✅ 모든 성분 수집용 set
    all_ingredients = set()

    # 1️⃣ 현재 복용 성분
    for item in current:
        all_ingredients.add(item["name"])

    # 2️⃣ 추천 제품 description에서 성분 키워드 감지
    for product in recommendations:
        desc = product.get("description", "").lower()

        # 테스트 로그 출력
        print(f"\n🧪 [테스트] 제품 설명:\n{desc[:300]}...")  # 앞 300자만 잘라서 출력

        for pair in GOOD_COMBOS + BAD_COMBOS:
            for nutrient in pair:
                if nutrient.lower() in desc:
                    all_ingredients.add(nutrient)

    # ✅ 테스트 로그: 감지된 성분 확인
    print(f"\n🧪 [테스트] 감지된 성분 목록: {sorted(all_ingredients)}")

    # 3️⃣ 조합 판단
    good_matches = []
    bad_matches = []

    for a in all_ingredients:
        for b in all_ingredients:
            if a == b:
                continue
            if (a, b) in GOOD_COMBOS or (b, a) in GOOD_COMBOS:
                good_matches.append(f"✅ {a} + {b}: 흡수 촉진 / 시너지 조합")
            if (a, b) in BAD_COMBOS or (b, a) in BAD_COMBOS:
                bad_matches.append(f"⚠️ {a} + {b}: 흡수 방해 또는 과잉 위험 조합")

    # 중복 제거
    good_matches = list(set(good_matches))
    bad_matches = list(set(bad_matches))

    # 결과 저장
    state["combinations"] = {
        "good": good_matches,
        "bad": bad_matches
    }

    return state