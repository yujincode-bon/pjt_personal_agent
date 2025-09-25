# nodes/symptom_llm_node.py
import os, json, re
from typing import List
from state import AgentState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# OPENAI_API_KEY 필요 (.env 로딩은 agent.py에서 하거나, 환경변수로 세팅)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM = """You are a nutrition domain assistant.
Given user's symptoms, extract a SHORT list (2~5) of nutrition ingredients that may help.
Return ONLY a compact JSON like: {"ingredients": ["Magnesium","Vitamin B6"]}."""

def _safe_extract_json(text: str) -> dict:
    # 응답 중 첫 JSON 블록만 파싱 시도
    m = re.search(r'\{.*\}', text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}

def symptom_llm_node(state: AgentState) -> AgentState:
    symptoms = state["profile"]["symptoms"]
    user = ", ".join(symptoms)

    msgs = [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"My symptoms: {user}")
    ]
    resp = llm.invoke(msgs)
    data = _safe_extract_json(resp.content)

    ingredients: List[str] = data.get("ingredients", []) if isinstance(data, dict) else []
    ingredients = [s.strip() for s in ingredients if isinstance(s, str) and s.strip()]

    # 비어있으면 fallback
    if not ingredients:
        # 최소 안전 넛지
        fallback = ["Magnesium", "Vitamin B6"] if "fatigue" in user.lower() else ["Vitamin C", "Zinc"]
        ingredients = fallback

    state["extracted_ingredients"] = ingredients
    return state