from agent import create_graph
from state import AgentState

if __name__ == "__main__":
    graph = create_graph()

    # 테스트 입력: 사용자 프로필
    test_state = AgentState(
        profile={
            "sex": "female",
            "age": 32,
            "symptoms": ["fatigue", "stress"],  # 증상 입력
            "recommendation_mode": "precise",   # "precise" 또는 "flexible"
            "current_intake": [
                {"name": "Vitamin C", "amount": 500, "unit": "mg"},
                {"name": "Zinc", "amount": 15, "unit": "mg"}
            ]
        }
    )

    result = graph.invoke(test_state)

    # ✅ 추천 결과
    print("\n✅ [추천 결과]")
    for i, rec in enumerate(result.get("recommendations", []), start=1):
        print(f"{i}. {rec['title']} ({rec['brand']}) - 평점 {rec['avg_rating']} / 리뷰 {rec['reviews_count']}")

    # ⚠️ 섭취 초과 감지
    print("\n⚠️ [섭취량 감지 결과]")
    for warning in result.get("warnings", []):
        print(warning)

    # 🔗 조합 평가
    print("\n🔗 [조합 평가 요약]")
    print(result.get("combination_prompt", "⚠️ 조합 프롬프트 없음"))