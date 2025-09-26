# nodes/combination_node.py
import json
from pathlib import Path
from state import AgentState

# ✅ 더 상세한 정보가 담긴 파일로 경로 변경
COMBO_PATH = Path("/Users/gim-yujin/Desktop/pjt_personal_agent/NutriBot/data/json/nutrient_combination_detailed.json")

def _load_combos() -> dict:
    with open(COMBO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def combination_node(state: AgentState) -> AgentState:
    combos = _load_combos()
    # ✅ 이제 각 조합은 상세 정보를 담은 dict 입니다.
    good_combos = combos.get("good", [])
    bad_combos  = combos.get("bad", [])

    # 현재 섭취 성분 + 추천 제품 설명에 언급된 성분 키워드(아주 단순 검출)
    profile = state["profile"]
    current = [c["name"] for c in profile.get("current_intake", []) if c.get("name")]
    recs = state.get("recommendations", [])

    mentioned = set(s for s in current)

    # ✅ 추천된 제품의 supplement_facts에서 직접 성분 이름을 추출
    for rec in recs:
        # ✅ 'parsed_ingredients'를 우선 사용하고, 없으면 'supplement_facts'를 사용
        ingredients = rec.get("parsed_ingredients") or rec.get("supplement_facts", [])
        for fact in ingredients:
            if fact.get("name"):
                mentioned.add(str(fact["name"]))

    # 조합 판단
    good_hits = []
    for combo in good_combos:
        if all(p in mentioned for p in combo["pair"]):
            good_hits.append(combo) # ✅ 상세 정보가 담긴 dict 전체를 추가

    bad_hits = []
    for combo in bad_combos:
        if all(p in mentioned for p in combo["pair"]):
            bad_hits.append(combo) # ✅ 상세 정보가 담긴 dict 전체를 추가

    state["combinations"] = {
        "good": sorted(good_hits),
        "bad": sorted(bad_hits),
    }
    return state