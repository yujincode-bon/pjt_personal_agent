# nodes/recommendation_node.py

from state import AgentState
from tools.db import get_supplements_from_db

def recommendation_node(state: AgentState) -> AgentState:
    profile = state.profile
    if not profile:
        raise ValueError("사용자 프로필이 없습니다.")

    symptoms = profile.symptoms
    sex = profile.sex
    age = profile.age

    # 1️⃣ 추천 제품 조회
    results = get_supplements_from_db(symptoms, sex, age)

    # 2️⃣ 중복 제거용 집합
    seen = set()
    top_recommendations = []

    for row in results:
        if isinstance(row, dict):
            title = str(row.get("title", "")).strip()
            brand = str(row.get("brand", "")).strip()

            # 중복 체크용 키
            unique_key = f"{title}_{brand}"
            if unique_key in seen:
                continue  # 중복된 제품은 건너뛰기
            seen.add(unique_key)

            rec = {
                "title": title,
                "brand": brand,
                "avg_rating": float(row.get("avg_rating", 0)),
                "reviews_count": int(row.get("reviews_count", 0)),
                "description": str(row.get("description", ""))
            }

        else:
            # dict가 아닌 경우도 방어적으로 처리
            rec = {
                "title": str(row),
                "brand": "",
                "avg_rating": 0,
                "reviews_count": 0,
                "description": ""
            }

        top_recommendations.append(rec)

    # 3️⃣ 추천 리스트 저장
    state.recommendations = top_recommendations
    return state