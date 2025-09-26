# nodes/recommendation_node.py
from state import AgentState
from tools.retrieval import get_supplements_by_faiss

def recommendation_node(state: AgentState) -> AgentState:
    symptoms = state["profile"]["symptoms"]

    # 벡터 검색
    results = get_supplements_by_faiss(symptoms)

    # 정규화 + 중복 제거
    seen = set()
    cleaned = []
    for r in results:
        product_code = r.get("product_code")
        if not product_code or product_code in seen:
            continue
        seen.add(product_code)
        # ✅ FAISS에서 반환된 전체 메타데이터(제품 정보)를 그대로 추가합니다.
        # 이 데이터에는 supplement_facts가 포함되어 있습니다.
        cleaned.append(r)

    # 평점 → 리뷰수 정렬
    cleaned.sort(key=lambda x: (x.get("avg_rating", 0), x.get("reviews_count", 0)), reverse=True)

    # 상위 5개
    state["recommendations"] = cleaned[:5]
    return state