# nodes/combination_node.py

from state import AgentState
import json

# 🔽 JSON 파일 로딩
with open("data/nutrient_combination_detailed.json", "r", encoding="utf-8") as f:
    COMBO_DATA = json.load(f)

GOOD_COMBOS = COMBO_DATA["good"]
BAD_COMBOS = COMBO_DATA["bad"]

def combination_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current = profile.get("current_intake", [])
    recommendations = state.get("recommendations", [])

    all_ingredients = set()

    # 1️⃣ 현재 복용 중인 성분
    for item in current:
        all_ingredients.add(item["name"])

    # 2️⃣ 추천 제품 설명에서 성분 추출
    for product in recommendations:
        desc = product.get("description", "").lower()
        for combo in GOOD_COMBOS + BAD_COMBOS:
            for nutrient in combo["pair"]:
                if nutrient.lower() in desc:
                    all_ingredients.add(nutrient)

    # 3️⃣ 조합 분석
    good_matches = []
    bad_matches = []

    for a in all_ingredients:
        for b in all_ingredients:
            if a == b:
                continue

            # 좋은 조합 탐색
            for combo in GOOD_COMBOS:
                if set(combo["pair"]) == set([a, b]):
                    msg = (
                        f"✅ {a} + {b}\n"
                        f"└ 설명: {combo['description']}\n"
                        f"└ 섭취 시간대: {combo['time']}\n"
                        f"└ 복용 팁: {combo['tips']}"
                    )
                    good_matches.append(msg)

            # 나쁜 조합 탐색
            for combo in BAD_COMBOS:
                if set(combo["pair"]) == set([a, b]):
                    msg = (
                        f"⚠️ {a} + {b}\n"
                        f"└ 설명: {combo['description']}\n"
                        f"└ 피해야 할 시간대: {combo['time']}\n"
                        f"└ 복용 팁: {combo['tips']}"
                    )
                    bad_matches.append(msg)

    # 중복 제거
    good_matches = list(set(good_matches))
    bad_matches = list(set(bad_matches))

    # 상태에 저장
    state["combinations"] = {
        "good": good_matches,
        "bad": bad_matches
    }

    return state