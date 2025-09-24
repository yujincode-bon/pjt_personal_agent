from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os

# 1. PostgreSQL에서 제품 데이터 로드
def load_supplements_from_db():
    engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT title, brand, avg_rating, reviews_count, description
            FROM supplements
        """))
        rows = result.fetchall()
        return rows

# 2. FAISS 인덱스 생성
def build_faiss_index():
    print("📦 DB에서 제품 정보 로딩 중...")
    rows = load_supplements_from_db()
    documents = []

    for row in rows:
        row = tuple(row)
        text = f"{row[0]} {row[4]}"  # title + description
        metadata = {
            "title": row[0],
            "brand": row[1],
            "avg_rating": float(row[2]) if row[2] else 0.0,
            "reviews_count": int(row[3]) if row[3] else 0,
            "description": row[4]
        }
        documents.append(Document(page_content=text, metadata=metadata))

    print(f"🧠 {len(documents)}개의 문서를 임베딩 중...")

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # ✅ 안전하게 저장 (pickle 사용 ❌)
    vectorstore.save_local("faiss_index")
    print("✅ FAISS 인덱스 저장 완료: faiss_index/")

# 3. FAISS 인덱스 로드 함수
def load_faiss_index():
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local("faiss_index", embeddings)

# ✅ 실행 스크립트
if __name__ == "__main__":
    build_faiss_index()