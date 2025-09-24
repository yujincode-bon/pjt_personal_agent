# nodes/intake_check_node.py

import json
from state import AgentState
from tools.names import clean_nutrient_name  # ✅ 정규화 함수 import

# RDA JSON 파일 로드
with open("../mappings/rda_korea_2020.json", "r") as f:
    RDA_TABLE = json.load(f)

def intake_check_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current = profile.get("current_intake", [])
    recommendations = state.get("recommendations", [])

    # 🔍 성분별 총 섭취량 계산
    total_intake = {}

    # 1️⃣ 현재 복용 중인 성분
    for item in current:
        raw = item.get("name", "")
        nutrient = clean_nutrient_name(raw)
        if not nutrient:
            continue

        total_intake[nutrient] = total_intake.get(nutrient, 0) + float(item.get("amount", 0))

    # 2️⃣ 추천된 제품에서 성분 추출
    for product in recommendations:
        desc = product.get("description", "")
        nutrient = clean_nutrient_name(desc)
        if nutrient:
            # 제품 description에는 수치는 없으므로 예시로 50mg 추가 (실제 파싱 필요)
            total_intake[nutrient] = total_intake.get(nutrient, 0) + 50

    # 3️⃣ 섭취량 분석 (RDA/UL 비교)
    warnings = []

    for nutrient, total in total_intake.items():
        if nutrient not in RDA_TABLE:
            continue

        rda = RDA_TABLE[nutrient].get("rda", 0)
        ul = RDA_TABLE[nutrient].get("ul", 99999)

        msg = None
        if total >= ul:
            msg = f"🚨 {nutrient}: 총 {total}mg (UL {ul} 초과!)"
        elif total >= rda * 2:
            msg = f"⚠️ {nutrient}: 총 {total}mg (RDA 2배 초과, UL 주의 필요)"
        elif total >= rda:
            msg = f"🔎 {nutrient}: 총 {total}mg (권장량 도달)"

        if msg:
            warnings.append(msg)

    state["warnings"] = warnings
    return state
