# state.py
from typing import TypedDict, Optional

# 현재 복용 성분 (사용자 입력)
class NutrientIntake(TypedDict):
    name: str
    amount: float  # mg 또는 IU
    unit: str

# 좋은/나쁜 조합 결과
class CombinationResult(TypedDict):
    good: list[str]
    bad: list[str]

# 사용자 프로필 정보
class Profile(TypedDict):
    sex: str
    age: int
    symptoms: list[str]
    current_intake: list[NutrientIntake]

# LangGraph 상태 구조
class AgentState(TypedDict):
    profile: Profile
    recommendations: Optional[list]
    warnings: Optional[list]
    combinations: Optional[CombinationResult]