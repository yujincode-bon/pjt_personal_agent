# agent.py

from langgraph.graph import StateGraph, END
from state import AgentState

# 노드 import
from nodes.goal_based_node import goal_based_node
from nodes.recommendation_node import recommendation_node
from nodes.intake_check_node import intake_check_node
from nodes.combination_node import combination_node
from nodes.combination_prompt_node import combination_prompt_node
from nodes.router_node import route_by_mode  # ✅ 분기 함수만 import


# ✅ LangGraph 정의
def create_graph():
    builder = StateGraph(AgentState)

    # 🔽 실제 노드만 등록 (router 노드 없음!)
    builder.add_node("goal_based", goal_based_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("intake_check", intake_check_node)
    builder.add_node("combination", combination_node)
    builder.add_node("combination_prompt", combination_prompt_node)

    # ✅ 조건 분기 (router는 단순한 키값)
    builder.add_conditional_edges(
        "router",         # <- 이름만 entry point로 씀
        route_by_mode,    # <- 조건 분기 함수
        {
            "goal_based": "goal_based",
            "recommendation": "recommendation"
        }
    )

    # ✅ 공통 흐름
    builder.add_edge("goal_based", "intake_check")
    builder.add_edge("recommendation", "intake_check")
    builder.add_edge("intake_check", "combination")
    builder.add_edge("combination", "combination_prompt")
    builder.add_edge("combination_prompt", END)

    builder.set_entry_point("router")
    return builder.compile()