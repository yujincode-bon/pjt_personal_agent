# tools/db.py

from tools.retrieval import get_supplements_by_faiss
from sqlalchemy import create_engine, text

# 1️⃣ FAISS 기반 검색 함수 (recommendation_node 에서 사용)
def get_supplements_from_db(symptoms: list[str], sex: str, age: int):
    return get_supplements_by_faiss(symptoms)


# 2️⃣ 전체 제품 불러오기 (goal_based_node 에서 사용)
def load_all_products():
    engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT title, brand, avg_rating, reviews_count, description
            FROM supplements
        """))
        rows = result.fetchall()
        return [
            {
                "title": row[0],
                "brand": row[1],
                "avg_rating": float(row[2]) if row[2] else 0.0,
                "reviews_count": int(row[3]) if row[3] else 0,
                "description": row[4] or ""
            }
            for row in rows
        ]