from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# 1. PostgreSQL에서 제품 데이터 로드
def load_supplements_from_db():
    engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")
    with engine.connect() as conn:
        # ✅ 3개 테이블을 JOIN하여 제품 정보와 성분 정보를 함께 가져옵니다.
        result = conn.execute(text("""
            SELECT 
                s.product_code, s.title, s.brand, s.avg_rating, s.reviews_count, s.description,
                i.name as ingredient_name, si.amount_per_serving, si.amount_unit, s.supplement_id
            FROM supplements
            LEFT JOIN supplement_ingredients si ON s.supplement_id = si.supplement_id
            LEFT JOIN ingredients i ON si.ingredient_id = i.ingredient_id
            ORDER BY s.product_code
        """))
        rows = result.fetchall()

        # ✅ 원본 JSON 데이터를 로드하여 parsed_ingredients 정보를 가져옵니다.
        parsed_json_path = Path(__file__).resolve().parent.parent / "data" / "json" / "parsed_supplements_output.json"
        with open(parsed_json_path, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)
        
        # product_code를 키로 하는 딕셔너리로 변환하여 쉽게 찾을 수 있도록 합니다.
        parsed_ingredients_map = {}
        for item in parsed_data:
            if item.get("Product code"):
                parsed_ingredients_map[item["Product code"]] = item.get("parsed_ingredients", [])

        # ✅ 가져온 데이터를 제품별로 그룹화하여 supplement_facts를 재구성합니다.
        products_dict = {}
        for row in rows:
            product_code = row[0]
            if product_code not in products_dict:
                products_dict[product_code] = {
                    "product_code": product_code,
                    "title": row[1],
                    "brand": row[2],
                    "avg_rating": float(row[3]) if row[3] else 0.0,
                    "reviews_count": int(row[4]) if row[4] else 0,
                    "description": row[5] or "",
                    "supplement_facts": [],
                    "parsed_ingredients": parsed_ingredients_map.get(product_code, []) # ✅ 파싱된 성분 정보 추가
                }
            
            if row[6]: # 성분 정보가 있는 경우
                products_dict[product_code]["supplement_facts"].append({
                    "name": row[6],
                    "amount": float(row[7]) if row[7] else 0.0,
                    "unit": row[8]
                })

        return list(products_dict.values())

# 2. FAISS 인덱스 생성
def build_faiss_index():
    print("📦 DB에서 제품 정보 로딩 중...")
    products = load_supplements_from_db()
    documents = []

    for product in products:
        text = f"{product['title']} {product['description']}"  # title + description
        # ✅ 전체 제품 정보를 메타데이터로 저장합니다.
        documents.append(Document(page_content=text, metadata=product))

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