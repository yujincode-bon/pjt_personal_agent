# nodes/goal_based_node.py

from state import AgentState
from tools.db import load_all_products
# ✅ 올바른 import
from mappings.symptom_mapping import SYMPTOM_INGREDIENT_MAP

def goal_based_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    symptoms = profile["symptoms"]

    # 1️⃣ 증상 기반 성분 추출
    target_ingredients = set()
    for symptom in symptoms:
        targets = SYMPTOM_INGREDIENT_MAP.get(symptom.lower(), [])
        target_ingredients.update(targets)

    # 2️⃣ 전체 제품 가져오기
    all_products = load_all_products()

    # 3️⃣ title + description에 성분 포함된 제품 필터링
    matched = []
    for product in all_products:
        text = f"{product.get('title', '')} {product.get('description', '')}".lower()
        for nutrient in target_ingredients:
            if nutrient.lower() in text:
                matched.append(product)
                break

    # 4️⃣ 정렬: 평점 → 리뷰 수
    matched.sort(key=lambda x: (x.get("avg_rating", 0), x.get("reviews_count", 0)), reverse=True)

    # 5️⃣ 상태에 저장
    state["goal_based_recommendations"] = matched
    state["recommendations"] = matched

    return state