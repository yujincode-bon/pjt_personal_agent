# nodes/combination_prompt_node.py

from state import AgentState

def combination_prompt_node(state: AgentState) -> AgentState:
    combos = state.get("combinations", {})
    good = combos.get("good", [])
    bad = combos.get("bad", [])

    messages = []

    if good:
        messages.append("👍 **함께 섭취하면 좋은 영양소 조합이 발견되었어요:**")
        for i, combo in enumerate(good, start=1):
            messages.append(f"{i}. {combo}")
    else:
        messages.append("ℹ️ 함께 섭취했을 때 특별히 좋은 조합은 없어요.")

    if bad:
        messages.append("\n⚠️ **주의가 필요한 영양소 조합이 있어요:**")
        for i, combo in enumerate(bad, start=1):
            messages.append(f"{i}. {combo}")
    else:
        messages.append("\n✅ 나쁜 조합은 발견되지 않았어요!")

    # 상태에 자연어 메시지 저장
    state["combination_prompt"] = "\n".join(messages)
    return state