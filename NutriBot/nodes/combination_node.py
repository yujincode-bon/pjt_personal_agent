# nodes/combination_node.py
import json
from pathlib import Path
from state import AgentState

COMBO_PATH = Path("/Users/gim-yujin/Desktop/pjt_personal_agent/NutriBot/data/json/nutrient_combination.json")

def _load_combos() -> dict:
    with open(COMBO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def combination_node(state: AgentState) -> AgentState:
    combos = _load_combos()
    good_pairs = set(tuple(x) for x in combos.get("good", []))
    bad_pairs  = set(tuple(x) for x in combos.get("bad", []))

    # 현재 섭취 성분 + 추천 제품 설명에 언급된 성분 키워드(아주 단순 검출)
    profile = state["profile"]
    current = [c["name"] for c in profile.get("current_intake", []) if c.get("name")]
    recs = state.get("recommendations", [])

    mentioned = set(s for s in current)

    # ✅ 추천된 제품의 supplement_facts에서 직접 성분 이름을 추출
    for rec in recs:
        for fact in rec.get("supplement_facts", []):
            if fact.get("name"):
                mentioned.add(fact["name"])

    # 조합 판단
    good_hits = {
        f"{a} + {b}" for a, b in good_pairs
        if a in mentioned and b in mentioned
    }
    bad_hits = {
        f"{a} + {b}" for a, b in bad_pairs
        if a in mentioned and b in mentioned
    }

    state["combinations"] = {
        "good": sorted(good_hits),
        "bad": sorted(bad_hits),
    }
    return state