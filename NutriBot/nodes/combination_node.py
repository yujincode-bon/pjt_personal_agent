# nodes/combination_node.py

from state import AgentState

# 조합 규칙 정의 (향후 JSON 로딩으로 대체 가능)
GOOD_COMBOS = [
    ("Vitamin C", "Iron"),
    ("Vitamin D", "Calcium"),
    ("Magnesium", "Vitamin B6"),
    ("Zinc", "Vitamin A"),
]

BAD_COMBOS = [
    ("Calcium", "Iron"),
    ("Zinc", "Magnesium"),
    ("Iron", "Coffee"),
    ("Vitamin C", "Copper"),
]

def _norm_name(n: str) -> str:
    """간단한 성분 이름 표준화"""
    return n.strip().title()

def combination_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current = profile.get("current_intake", [])
    recommendations = state.get("recommendations", [])

    all_ingredients = set()

    # 1️⃣ 현재 복용 성분
    for item in current:
        all_ingredients.add(_norm_name(item.get("name", "")))

    # 2️⃣ 추천 제품에서 성분 추출
    for rec in recommendations:
        # parsed_ingredients 기준으로 추출
        ingredients = rec.get("parsed_ingredients") or rec.get("supplement_facts", [])
        for ing in ingredients:
            name = _norm_name(ing.get("name", ""))
            if name:
                all_ingredients.add(name)

    # 3️⃣ 조합 판단
    good_matches = []
    bad_matches = []

    ingredient_list = list(all_ingredients)

    for i in range(len(ingredient_list)):
        for j in range(i + 1, len(ingredient_list)):
            a = ingredient_list[i]
            b = ingredient_list[j]

            if (a, b) in GOOD_COMBOS or (b, a) in GOOD_COMBOS:
                good_matches.append(f"{a} + {b}")
            if (a, b) in BAD_COMBOS or (b, a) in BAD_COMBOS:
                bad_matches.append(f"{a} + {b}")

    # 중복 제거
    state["combinations"] = {
        "good": list(set(good_matches)),
        "bad": list(set(bad_matches)),
    }

    return state