# nodes/intake_check_node.py
import json
import re
from pathlib import Path
from state import AgentState

# RDA 기준 경로
RDA_PATH = Path("data/json/rda.json")

def _load_rda_table() -> dict:
    if not RDA_PATH.exists():
        print(f"❗ RDA 파일 없음: {RDA_PATH}")
        return {}
    with open(RDA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _norm_name(name: str) -> str:
    """영양소 이름 정규화"""
    name = name.lower().strip()
    mapping = {
        "vit c": "Vitamin C", "vitamin c": "Vitamin C", "ascorbic acid": "Vitamin C",
        "vit d": "Vitamin D", "vitamin d": "Vitamin D", "cholecalciferol": "Vitamin D",
        "vit b6": "Vitamin B6", "vitamin b6": "Vitamin B6", "pyridoxine": "Vitamin B6",
        "zinc": "Zinc", "magnesium": "Magnesium", "iron": "Iron", "calcium": "Calcium",
    }
    return mapping.get(name, name.title())

def _parse_facts_from_raw_line(raw_line: str) -> list[dict]:
    """raw_line에서 성분 파싱 (예: 'Vitamin C 500 mg')"""
    if not raw_line:
        return []

    pattern = re.compile(r'([a-zA-Z\s\(\)%]+?)\s+([\d\.]+)\s*(mg|mcg|g|iu|%)\b', re.IGNORECASE)
    matches = pattern.findall(raw_line)

    results = []
    for match in matches:
        name, amount, unit = match
        name = _norm_name(name)
        try:
            amount = float(amount)
        except:
            continue
        results.append({"name": name, "amount": amount, "unit": unit})
    return results

def _get_rda_value(rda_data: dict, sex: str, age: int) -> float | None:
    """성별/나이대에 맞는 RDA or UL 값 추출"""
    age_group_key = ""
    if 19 <= age <= 30:
        age_group_key = f"{sex}_19-30"
    elif age >= 31:
        age_group_key = f"{sex}_31+"

    return rda_data.get(age_group_key) or rda_data.get(f"{sex}_default") or rda_data.get("default")

def intake_check_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    sex = profile.get("sex", "")
    age = profile.get("age", 0)
    current = profile.get("current_intake", [])

    RDA_TABLE = _load_rda_table()
    warnings = []
    all_items = list(current)

    for rec in state.get("recommendations", []):
        # parsed_ingredients 우선 사용
        facts = rec.get("parsed_ingredients") or rec.get("supplement_facts", [])

        # supplement_facts가 없고 raw_line만 있는 경우
        if not facts and "raw_line" in rec:
            facts = _parse_facts_from_raw_line(rec["raw_line"])

        all_items.extend(facts)

    # 총 섭취량 집계
    totals = {}  # nutrient → {"amount": float, "unit": str}
    for item in all_items:
        n = _norm_name(str(item.get("name", "")))
        amt = float(item.get("amount", 0) or 0)
        unit = str(item.get("unit", "")).lower()

        if not n or amt <= 0:
            continue

        if n not in totals:
            totals[n] = {"amount": 0.0, "unit": unit}
        totals[n]["amount"] += amt

    # 초과 여부 검사
    for n, v in totals.items():
        nutrient_info = RDA_TABLE.get(n)
        if not nutrient_info:
            continue

        rda = _get_rda_value(nutrient_info.get("rda", {}), sex, age)
        ul = _get_rda_value(nutrient_info.get("ul", {}), sex, age)
        amt = v["amount"]

        if ul and amt > ul:
            warnings.append(
                f"🚨 {n}: 총 섭취량 {amt}{v['unit']}이(가) 상한섭취량({ul}{nutrient_info['unit']})을 초과할 수 있습니다."
            )
        elif rda and amt > rda * 2:
            warnings.append(
                f"⚠️ {n}: 총 섭취량 {amt}{v['unit']}이(가) 권장섭취량({rda}{nutrient_info['unit']})의 2배를 초과합니다. 과다 섭취에 주의하세요."
            )

    state["warnings"] = warnings
    return state