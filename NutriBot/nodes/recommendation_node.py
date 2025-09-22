from state import AgentState
from tools.db import get_supplements_from_db

def recommendation_node(state: AgentState) -> AgentState:
    profile = state.profile
    symptoms = profile.symptoms
    sex = profile.sex
    age = profile.age

    results = get_supplements_from_db(symptoms, sex, age)
    top_recommendations = []

    for row in results:
        if isinstance(row, dict):
            rec = {
                "title": str(row.get("title", "")),
                "brand": str(row.get("brand", "")),
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

    state.recommendations = top_recommendations
    return state