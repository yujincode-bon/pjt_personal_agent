# state.py

from typing import List, Optional, Literal
from pydantic import BaseModel

# 사용자 프로필 정의
class UserProfile(BaseModel):
    sex: Literal["male", "female"]
    age: int
    symptoms: List[str]
    current_intake: Optional[List[str]] = []

# 에이전트 상태 정의
class AgentState(BaseModel):
    profile: Optional[UserProfile] = None
    recommendations: Optional[List[dict]] = None
    risk_report: Optional[str] = None
    guideline: Optional[str] = None
    answer: Optional[str] = None