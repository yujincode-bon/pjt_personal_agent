# agent.py

from langgraph.graph import StateGraph, END
from state import AgentState

# 노드 import
from nodes.goal_based_node import goal_based_node
from nodes.recommendation_node import recommendation_node
from nodes.intake_check_node import intake_check_node
from nodes.combination_node import combination_node
from nodes.router_node import router_node  # ✅ 조건 분기 함수

def create_graph():
    builder = StateGraph(AgentState)

    # ✅ ✅ ✅ 꼭 필요함 (버전 0.0.x에서만)
    builder.add_node("router", router_node)

    # 나머지 노드 등록
    builder.add_node("goal_based", goal_based_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("intake_check", intake_check_node)
    builder.add_node("combination", combination_node)

    # 조건 분기 연결
    builder.add_conditional_edges(
        "router",  # source node
        router_node,
        {
            "goal_based": "goal_based",
            "recommendation": "recommendation"
        }
    )

    builder.add_edge("goal_based", "intake_check")
    builder.add_edge("recommendation", "intake_check")
    builder.add_edge("intake_check", "combination")
    builder.add_edge("combination", END)

    builder.set_entry_point("router")  # Entry는 문자열
    return builder.compile()

if __name__ == "__main__":
    graph = create_graph()

    test_state = AgentState(
        profile={
            "sex": "female",
            "age": 29,
            "symptoms": ["fatigue", "stress"],
            "recommendation_mode": "precise",  # 또는 "flexible"
            "current_intake": [
                {"name": "Vitamin C", "amount": 1000, "unit": "mg"},
                {"name": "Zinc", "amount": 25, "unit": "mg"}
            ]
        }
    )

    result = graph.invoke(test_state)

    # ✅ 추천 결과 출력
    print("\n✅ 추천 결과:")
    for i, rec in enumerate(result.get("recommendations", []), start=1):
        print(f"{i}. {rec['title']} ({rec['brand']}) - 평점 {rec['avg_rating']} / 리뷰 {rec['reviews_count']}")

    # ⚠️ 섭취 감지
    print("\n⚠️ 섭취량 감지 결과:")
    for warning in result.get("warnings", []):
        print(warning)

    # 🔗 조합 평가
    print("\n🔗 성분 조합 평가:")
    combos = result.get("combinations", {})
    print("✅ 좋은 조합:")
    for line in combos.get("good", []):
        print(line)
    print("❌ 나쁜 조합:")
    for line in combos.get("bad", []):
        print(line)