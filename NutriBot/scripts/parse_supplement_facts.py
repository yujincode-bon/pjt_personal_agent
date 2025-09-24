# scripts/parse_supplement_facts.py
import sys
from pathlib import Path

# 상위 디렉토리(NutriBot/)를 모듈 경로에 추가
sys.path.append(str(Path(__file__).resolve().parent.parent))


import json
from tools.parsers import parse_raw_line
from pathlib import Path

INPUT_PATH = Path("data/supplement_rag_data_merged_with_reviews.json")
OUTPUT_PATH = Path("data/parsed_supplement_facts.json")

parsed_all = []

with open(INPUT_PATH, "r") as f:
    data = json.load(f)

for product in data:
    brand = product.get("brand", "")
    title = product.get("title", "")

    facts = product.get("supplement_facts", [])
    for item in facts:
        raw = item.get("raw_line", "")
        parsed = parse_raw_line(raw)

        for nutrient in parsed:
            nutrient["brand"] = brand
            nutrient["title"] = title
            parsed_all.append(nutrient)

# ✅ JSON으로 저장
with open(OUTPUT_PATH, "w") as f:
    json.dump(parsed_all, f, indent=2, ensure_ascii=False)

print(f"✅ {len(parsed_all)}개 성분 파싱 완료 → {OUTPUT_PATH.name}")