# nodes/combination_prompt_node.py
from state import AgentState

def combination_prompt_node(state: AgentState) -> AgentState:
    combos = state.get("combinations", {"good": [], "bad": []})
    good = combos.get("good", [])
    bad = combos.get("bad", [])

    lines = []
    if good:
        lines.append("👍 함께 섭취하면 좋은 조합:")
        for i, g in enumerate(good, 1):
            lines.append(f"  {i}. {g}")
    else:
        lines.append("ℹ️ 함께 섭취했을 때 특별히 좋은 조합은 없어요.")

    if bad:
        lines.append("\n⚠️ 주의가 필요한 조합:")
        for i, b in enumerate(bad, 1):
            lines.append(f"  {i}. {b}")
    else:
        lines.append("\n✅ 나쁜 조합은 발견되지 않았어요!")

    state["combination_prompt"] = "\n".join(lines)
    return state