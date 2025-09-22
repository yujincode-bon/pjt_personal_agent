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

    # 💬 DB에서 추천 제품 리스트 받아오기
    results = get_supplements_from_db(symptoms, sex, age)

    top_recommendations = []

    for row in results:
        # ✅ row가 dict인 경우
        if isinstance(row, dict):
            rec = row

        # ✅ row가 tuple/list인 경우: 각 필드 수동 매핑
        elif isinstance(row, (tuple, list)):
            rec = {
                "title": row[0],
                "brand": row[1],
                "avg_rating": row[2],
                "reviews_count": row[3],
                "description": row[4]
            }
        # ✅ row가 문자열 또는 그 외인 경우
        else:
            rec = {
                "title": str(row),
                "brand": "",
                "avg_rating": 0,
                "reviews_count": 0,
                "description": ""
            }

        top_recommendations.append(rec)

    # 결과를 상태에 저장
    state.recommendations = top_recommendations
    return state