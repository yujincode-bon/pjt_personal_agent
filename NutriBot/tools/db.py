# tools/db.py
import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text

# ⚠️ 벡터 검색은 tools/retrieval.get_supplements_by_faiss를 사용
#   (faiss_index 디렉토리와 OpenAI API KEY 필요)
from tools.retrieval import get_supplements_by_faiss

DB_URL = os.getenv("DB_URL", "postgresql://postgres:67368279@localhost:5432/NutriBot")
_engine = create_engine(DB_URL)

def load_all_products() -> List[Dict[str, Any]]:
    """
    DB에서 전체 제품을 dict 리스트로 가져온다.
    """
    with _engine.connect() as conn:
        result = conn.execute(text("""
            SELECT title, brand, avg_rating, reviews_count, description
            FROM supplements
        """))
        rows = result.fetchall()

    products = []
    for r in rows:
        r = tuple(r)
        products.append({
            "title": str(r[0]) if len(r) > 0 else "",
            "brand": str(r[1]) if len(r) > 1 else "",
            "avg_rating": float(r[2]) if len(r) > 2 and r[2] is not None else 0.0,
            "reviews_count": int(r[3]) if len(r) > 3 and r[3] is not None else 0,
            "description": str(r[4]) if len(r) > 4 and r[4] is not None else "",
        })
    return products

def get_supplements_from_db(ingredients: list[str], sex: str, age: int) -> List[Dict[str, Any]]:
    """
    FAISS 유사도 검색으로 제품 후보를 찾는다.
    ⚠️ 이제 symptoms 대신 LLM이 추출한 ingredients를 사용합니다.
    """
    return get_supplements_by_faiss(ingredients, k=10)  # 반환: [{title, brand, avg_rating, reviews_count, description, ...}, ...]