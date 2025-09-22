# agent.py

from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.recommendation_node import recommendation_node

def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("recommendation", recommendation_node)
    builder.set_entry_point("recommendation")
    builder.add_edge("recommendation", END)
    return builder.compile()

if __name__ == "__main__":
    graph = create_graph()

    test_state = AgentState(
        profile={
            "sex": "female",
            "age": 29,
            "symptoms": ["fatigue", "sleep"]
        }
    )

    result = graph.invoke(test_state)
  
    print("\n✅ 추천 결과:")
    for i, rec in enumerate(result["recommendations"], start=1):
        print(f"{i}. {rec['title']} ({rec['brand']}) - 평점 {rec['avg_rating']} / 리뷰 {rec['reviews_count']}")#$