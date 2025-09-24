# nodes/recommendation_node.py

from state import AgentState
from tools.db import get_supplements_from_db

def recommendation_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    symptoms = profile["symptoms"]
    sex = profile["sex"]
    age = profile["age"]

    # 1️⃣ FAISS 기반 추천 제품 검색
    results = get_supplements_from_db(symptoms, sex, age)

    seen = set()
    top_recommendations = []

    for row in results:
        if isinstance(row, dict):
            title = str(row.get("title", "")).strip()
            brand = str(row.get("brand", "")).strip()
            unique_key = f"{title}_{brand}"

            if unique_key in seen:
                continue
            seen.add(unique_key)

            rec = {
                "title": title,
                "brand": brand,
                "avg_rating": float(row.get("avg_rating", 0)),
                "reviews_count": int(row.get("reviews_count", 0)),
                "description": str(row.get("description", ""))
            }
        else:
            rec = {
                "title": str(row),
                "brand": "",
                "avg_rating": 0,
                "reviews_count": 0,
                "description": ""
            }

        top_recommendations.append(rec)

    # 2️⃣ 평점 + 리뷰 수 기준 정렬
    top_recommendations.sort(
        key=lambda x: (x["avg_rating"], x["reviews_count"]),
        reverse=True
    )

    # 3️⃣ 상태에 저장
    state["recommendations"] = top_recommendations
    return state