# nodes/intake_check_node.py
import json
from pathlib import Path
from state import AgentState

# RDA 테이블 파일 경로 (프로젝트 루트 기준)
RDA_PATH = Path("/Users/gim-yujin/Desktop/pjt_personal_agent/NutriBot/data/json/nutrient_combination.json")
# ⚠️ 경로 수정: 영양소 조합 파일이 아닌 RDA 정보 파일을 사용하도록 변경
RDA_PATH = Path("/Users/gim-yujin/Desktop/pjt_personal_agent/NutriBot/data/json/rda.json")

def _load_rda_table() -> dict:
    if not RDA_PATH.exists():
        print(f"⚠️ 경고: RDA 파일({RDA_PATH})을 찾을 수 없습니다.")
        return {}
    with open(RDA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _norm_name(s: str) -> str:
    s = s.lower().strip()
    # 아주 간단한 표준화(필요시 확장)
    mapping = {
        "vitamin c": "Vitamin C",
        "vit c": "Vitamin C",
        "ascorbic acid": "Vitamin C",
        "zinc": "Zinc",
        "magnesium": "Magnesium",
        "vitamin b6": "Vitamin B6",
        "vit b6": "Vitamin B6",
        "iron": "Iron",
        "calcium": "Calcium",
        "vitamin d": "Vitamin D",
        "vit d": "Vitamin D",
    }
    return mapping.get(s, s.title())

def _get_rda_value(rda_data: dict, sex: str, age: int) -> float | None:
    """성별과 나이에 맞는 RDA/UL 값을 찾습니다."""
    if not rda_data:
        return None

    # 나이대별 키 생성 (예: male_19-30, female_31+)
    age_group_key = ""
    if 19 <= age <= 30:
        age_group_key = f"{sex}_19-30"
    elif age >= 31:
        age_group_key = f"{sex}_31+"

    # 구체적인 키 -> 성별 기본값 -> 전체 기본값 순으로 탐색
    return rda_data.get(age_group_key) or \
           rda_data.get(f"{sex}_default") or \
           rda_data.get("default")

def intake_check_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current = profile.get("current_intake", [])

    RDA_TABLE = _load_rda_table()
    warnings = []

    # 추천된 제품의 성분 정보도 총 섭취량에 합산
    all_intake_items = list(current)
    for rec in state.get("recommendations", []):
        all_intake_items.extend(rec.get("supplement_facts", []))

    # 총 섭취량 집계
    totals = {}  # {nutrient: {"amount": float, "unit": str}}
    for item in all_intake_items:
        n = _norm_name(str(item.get("name", "")))
        amt = float(item.get("amount", 0) or 0)
        unit = str(item.get("unit", "")).lower()

        if not n or amt <= 0:
            continue

        if n not in totals:
            totals[n] = {"amount": 0.0, "unit": unit}
        totals[n]["amount"] += amt

    # RDA/UL 비교
    for n, v in totals.items():
        rda_info = RDA_TABLE.get(n, {})
        # 예: {"unit":"mg","rda":{"female_29":...},"ul":{"female_29":...}} 등 구조가 다양할 수 있음
        # 여기서는 단순화: rda, ul 키가 바로 float라고 가정, 없으면 스킵
        rda = rda_info.get("rda")
        ul = rda_info.get("ul")
        unit_rda = rda_info.get("unit", v["unit"])
        nutrient_info = RDA_TABLE.get(n)
        if not nutrient_info:
            continue

        # 단위 무시/가정 (실서비스에서는 반드시 단위 변환 로직 필요)
        rda = _get_rda_value(nutrient_info.get("rda", {}), profile["sex"], profile["age"])
        ul = _get_rda_value(nutrient_info.get("ul", {}), profile["sex"], profile["age"])

        # 🚨 단위 변환 로직은 단순화를 위해 생략 (실제 서비스에서는 필수)
        amt = v["amount"]

        if isinstance(rda, (int, float)) and amt > rda * 2:
            warnings.append(f"⚠️ {n}: 총 {amt}{v['unit']} (RDA 2배 초과, UL 주의 필요)")
        elif isinstance(ul, (int, float)) and amt > ul:
            warnings.append(f"⚠️ {n}: 총 {amt}{v['unit']} (UL 초과 가능성)")
        if ul and amt > ul:
            warnings.append(f"🚨 {n}: 총 섭취량 {amt}{v['unit']}이(가) 상한섭취량({ul}{nutrient_info['unit']})을 초과할 수 있습니다.")
        elif rda and amt > rda * 2:
            warnings.append(f"⚠️ {n}: 총 섭취량 {amt}{v['unit']}이(가) 권장섭취량({rda}{nutrient_info['unit']})의 2배를 초과합니다. 과다 섭취에 주의하세요.")

    state["warnings"] = warnings
    return state