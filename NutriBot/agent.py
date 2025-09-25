# agent.py
import os
from dotenv import load_dotenv
load_dotenv()  # OPENAI_API_KEY, DB_URL 등

from langgraph.graph import StateGraph, END
from state import AgentState

# 노드들
from nodes.symptom_llm_node import symptom_llm_node
from nodes.recommendation_node import recommendation_node
from nodes.intake_check_node import intake_check_node
from nodes.combination_node import combination_node
from nodes.combination_prompt_node import combination_prompt_node

def create_graph():
    builder = StateGraph(AgentState)

    builder.add_node("symptom_llm", symptom_llm_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("intake_check", intake_check_node)
    builder.add_node("combination", combination_node)
    builder.add_node("combination_prompt", combination_prompt_node)

    builder.set_entry_point("symptom_llm")
    builder.add_edge("symptom_llm", "recommendation")
    builder.add_edge("recommendation", "intake_check")
    builder.add_edge("intake_check", "combination")
    builder.add_edge("combination", "combination_prompt")
    builder.add_edge("combination_prompt", END)

    return builder.compile()

if __name__ == "__main__":
    graph = create_graph()

    # ✅ 테스트 입력
    test_state = AgentState(
        profile={
            "sex": "female",
            "age": 29,
            "symptoms": ["fatigue", "sleep"],
            "current_intake": [
                {"name": "Vitamin C", "amount": 1000, "unit": "mg"},
                {"name": "Zinc", "amount": 25, "unit": "mg"}
            ]
        }
    )

    result = graph.invoke(test_state)

    print("\n✅ LLM 추출 성분:", result.get("extracted_ingredients", []))

    print("\n✅ 추천 결과:")
    for i, rec in enumerate(result.get("recommendations", []), start=1):
        print(f"{i}. {rec['title']} ({rec['brand']}) - 평점 {rec['avg_rating']} / 리뷰 {rec['reviews_count']}")

    print("\n⚠️ 섭취량 감지 결과:")
    for w in result.get("warnings", []):
        print(w)

    print("\n🔗 조합 평가 요약:")
    print(result.get("combination_prompt", "조합 프롬프트가 없습니다."))