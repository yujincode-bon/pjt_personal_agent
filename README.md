# pjt_personal_agent
Sesac AI 기반 데이터 분석가 양성 과정 1기 최종 프로젝트 

물론이죠, 유진님.
아래는 유진님의 **LangGraph 기반 맞춤형 영양제 추천 챗봇 프로젝트(MVP)**를 위한 완성형 README.md 템플릿입니다.

⸻

🧠 NutriOne: 맞춤형 영양제 추천 챗봇 (LangGraph + RAG 기반)

당신의 건강 목표에 맞춰 가장 안전한 단일 영양제를 추천하는 대화형 에이전트
LLM · LangGraph · 라우터 · RAG · Chroma 기반으로 설계된 스마트 챗봇 MVP

⸻

🚀 프로젝트 개요

NutriOne은 사용자의 건강 목표, 성별, 연령, 복용 중인 성분 정보를 바탕으로
과다 섭취를 피하면서 부족한 영양소를 보완할 수 있는 단일 제품 1개를 추천해주는 LangGraph 기반 챗봇 시스템입니다.

이 시스템은 다음과 같은 기술적 도전 과제를 해결합니다:
	•	✅ 자연어 건강 목표를 영양소로 변환 (LLM)
	•	✅ 현재 복용 중인 성분의 과다 섭취 방지 (라우터/필터)
	•	✅ 제품 정보(JSON)에서 적절한 상품 필터링
	•	✅ 추천 사유를 PDF 근거 기반으로 RAG + 요약

⸻

🎯 핵심 기능 (MVP)

단계	기능 설명
A-1	사용자의 성별, 나이, 건강 목표 입력
A-2	사용자가 복용 중인 영양제를 선택하거나 생략 가능
B-1	목표에 따라 추천 성분 도출 (LLM or 매핑)
B-2	현재 복용 성분과 중복되는 성분 제거 (UL 체크 생략 가능)
C-1	부족 성분을 가장 많이 포함한 단일 제품 1개 추천
C-2	해당 성분이 추천되는 이유를 PDF(RAG) 기반으로 자연어 설명
D-1	대화형 응답 생성 → “왜 이 제품을 추천하는지”를 명확히 설명


⸻

🧱 시스템 아키텍처 (LangGraph)

UserInputNode
  ↓
IntakeRouterNode ──────────────┐
  ↓                            ↓
(섭취 없음)                IntakeExpandByProductNode
  ↓                            ↓
GoalToIngredientsNode <───────┘
  ↓
IntakeSafetyFilterNode
  ↓
ProductRankerNode
  ↓
ReasonRAGNode (Chroma + LLM)
  ↓
FinalAnswerNode

📌 라우터 기반으로 섭취 입력 유무에 따라 흐름이 달라지며,
추천 사유는 PDF 근거 문장을 RAG로 검색 + 요약하여 신뢰성 있는 답변을 제공합니다.

⸻

📦 사용 데이터

데이터	설명
parsed_supplements_output.json	실제 iHerb 상품 데이터 (성분명, 용량 포함)
2020 한국인 영양소 섭취기준 (비타민/무기질)	PDF로 제공된 영양소 권장량 및 효능 근거 자료
(선택) nutrient_rda.json	성별/연령별 RDA/UL 정보 (정적 JSON 방식)


⸻

🧠 기술 스택

항목	설명
LangGraph	에이전트 구성 및 노드 분기 흐름
LLM (OpenAI)	증상 → 성분 추론 / 자연어 응답 생성
Chroma	PDF 기반 벡터 DB 저장소 (청크화 & 검색)
RAG	PDF 근거 문장을 찾아 추천 사유 생성
LangSmith	프롬프트/응답 추적 및 실행 로그 분석


⸻

🧪 실행 방법

# 의존성 설치
pip install -r requirements.txt

# Chroma로 PDF 벡터화
python app/rag/ingest_pdf.py

# LangGraph 에이전트 실행
python app/main.py


⸻

✅ MVP 데모 예시

사용자 입력

{
  "sex": "female",
  "age": 29,
  "goal": "면역",
  "current_intake": []
}

최종 응답 예시

{
  "recommended_product": "Immune-C + Zinc",
  "matched_ingredients": ["Vitamin C", "Zinc"],
  "reason": "비타민 C와 아연은 면역세포 기능을 향상시켜 감염 예방에 기여합니다. (출처: 2020 섭취기준 p.44)",
  "notes": "현재 복용 중인 성분과 중복되지 않아 안전합니다."
}


⸻

⚠️ 한계 및 어려움
	•	복용 성분의 용량 미입력 시 UL 체크 불가 → 현재는 “중복 제거”로 최소 안전성만 확보
	•	PDF 근거 문단이 표 형식일 경우 RAG가 제대로 작동하지 않는 이슈
	•	제품 DB에 동일 성분명도 표기 편차 존재 → 정규화 룰이 추가로 필요

⸻

🔮 향후 확장 방향

기능	설명
✅ RDA/UL 수치 비교 자동화	정적 JSON 또는 PDF RAG에서 수치 추출 및 비교
✅ 리뷰 요약	제품 리뷰 기반 효능 요약 또는 부작용 탐지
✅ 성분 상호작용 분석	아연-구리, 칼슘-철분 등의 섭취 주의 조합 안내
✅ Top-N 조합 추천	단일 제품 한계 → 2~3개 조합 추천으로 확장
✅ 사용자 피드백 기반 fine-tune	추천 정확도 향상 및 UX 개선


⸻

📁 디렉토리 구조

📦 app/
 ┣ nodes/              # LangGraph 노드 정의
 ┣ rag/                # PDF → 청크 분리 → Chroma 인덱싱
 ┣ data/               # 제품 JSON, PDF, 벡터 DB
 ┣ schemas/            # 사용자 입력/출력 구조
 ┗ main.py             # 에이전트 실행


⸻

📊 LangSmith 모니터링
	•	모든 실행 흐름은 LangSmith에서 LangGraph 기반 트레이스로 기록
	•	프롬프트 입력/출력, 추천 사유 생성 등의 디버깅 및 분석 가능

⸻

🧾 라이선스 & 출처
	•	제품 데이터 출처: iHerb.com
	•	섭취 기준: [2020 한국인 영양소 섭취기준 (KDRIs)]
	•	라이선스: MIT 
