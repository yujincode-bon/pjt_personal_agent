# intake_check
# 사용자 복용 + 추천 성분 → RDA/UL 기준 초과 감지


from state import AgentState

NUTRIENT_LIMITS = {
    "Vitamin C": {"rda": 100, "ul": 2000, "unit": "mg"},
    "Zinc": {"rda": 10, "ul": 40, "unit": "mg"},
    "Vitamin D": {"rda": 15, "ul": 100, "unit": "mcg"},
}

def intake_check_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    current_intake = profile.get("current_intake", [])
    recommendations = state.get("recommendations", [])

    total_intake = {}

    for item in current_intake:
        name = item["name"]
        amount = item["amount"]
        total_intake[name] = total_intake.get(name, 0) + amount

    for product in recommendations:
        desc = product.get("description", "")
        for nutrient in NUTRIENT_LIMITS:
            if nutrient.lower() in desc.lower():
                total_intake[nutrient] = total_intake.get(nutrient, 0) + (
                    NUTRIENT_LIMITS[nutrient]["rda"] * 0.5
                )

    warnings = []
    for nutrient, total in total_intake.items():
        limits = NUTRIENT_LIMITS.get(nutrient)
        if not limits:
            continue

        if total > limits["ul"]:
            warnings.append(f"❗ {nutrient}: 총 {total}{limits['unit']} (UL {limits['ul']}{limits['unit']} 초과)")
        elif total > limits["rda"] * 2:
            warnings.append(f"⚠️ {nutrient}: 총 {total}{limits['unit']} (RDA 2배 초과, UL 주의 필요)")
        elif total > limits["rda"]:
            warnings.append(f"ℹ️ {nutrient}: 총 {total}{limits['unit']} (RDA 초과)")

    state["warnings"] = warnings
    return state