# # tools/db.py
from tools.retrieval import get_supplements_by_faiss

def get_supplements_from_db(symptoms: list[str], sex: str, age: int):
    return get_supplements_by_faiss(symptoms)












# from sqlalchemy import create_engine, text

# # ✅ PostgreSQL 연결
# engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")

# def get_supplements_from_db(symptoms: list[str], sex: str, age: int):
#     symptom_query = "%{}%".format("%".join(symptoms))

#     query = text(f"""
#         SELECT title, brand, avg_rating, reviews_count, description
#         FROM supplements
#         WHERE title ILIKE :query OR description ILIKE :query
#         ORDER BY avg_rating DESC, reviews_count DESC
#         LIMIT 5;
#     """)

#     with engine.connect() as conn:
#         result = conn.execute(query, {"query": symptom_query})
#         rows = result.fetchall()
#         return rows  # ✅ row: tuple(title, brand, ...)