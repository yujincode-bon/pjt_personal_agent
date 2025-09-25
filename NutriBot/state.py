# state.py
from typing import TypedDict, Optional

class NutrientIntake(TypedDict):
    name: str
    amount: float   # mg/mcg/IU/g 등
    unit: str

class CombinationResult(TypedDict):
    good: list[str]
    bad: list[str]

class Profile(TypedDict):
    sex: str
    age: int
    symptoms: list[str]                # 사용자가 말한 증상 키워드
    current_intake: list[NutrientIntake]

class AgentState(TypedDict, total=False):
    profile: Profile

    # LLM이 뽑아준 타겟 성분
    extracted_ingredients: list[str]

    # 추천 결과 (제품 dict 리스트)
    recommendations: list[dict]

    # 섭취량 경고 메시지들
    warnings: list[str]

    # 성분 조합 결과 + 자연어 요약
    combinations: CombinationResult
    combination_prompt: str