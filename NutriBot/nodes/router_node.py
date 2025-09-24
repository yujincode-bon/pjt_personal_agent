# nodes/router_node.py

from state import AgentState

def router_node(state: AgentState) -> str:
    """
    사용자의 추천 방식을 읽고 분기 문자열을 반환합니다.
    반환값은 "goal_based" 또는 "recommendation"이어야 합니다.
    """
    mode = state["profile"].get("recommendation_mode", "precise").lower()
    print(f"📍 [Router] 추천 방식 선택됨: {mode}")
    return "goal_based" if mode == "precise" else "recommendation"