# nodes/router_node.py

from state import AgentState

def route_by_mode(state: AgentState) -> str:
    mode = state["profile"].get("recommendation_mode", "precise").lower()
    print(f"📍 [Router] 추천 방식 선택됨: {mode}")
    return "goal_based" if mode == "precise" else "recommendation"