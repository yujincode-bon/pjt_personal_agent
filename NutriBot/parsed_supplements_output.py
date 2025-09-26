import json
import re
from tqdm import tqdm

# 1. 파싱 함수 정의
def parse_supplement_facts_from_raw_line(raw_line):
    # 숫자+단위 추출 패턴 예: 500 mg, 2.5 g, 1000 IU 등
    amount_unit_pattern = r'(?P<amount>\d{1,4}(?:[.,]\d{1,2})?)\s?(?P<unit>mg|g|mcg|μg|IU|iu|%)'

    # 단어(성분명) + 수치+단위 조합 패턴
    combined_pattern = r'(?P<name>[A-Za-z0-9αβμ%(),\- +]+?)\s*' + amount_unit_pattern

    matches = re.finditer(combined_pattern, raw_line)

    parsed = []
    for match in matches:
        name = match.group('name').strip()
        name = re.sub(r'[^a-zA-Z0-9 +\-(),%]', '', name)
        name = name.replace("Daily Value", "").strip()  # 불필요한 키워드 제거
        try:
            amount = float(match.group('amount').replace(",", ""))
        except:
            continue
        unit = match.group('unit').lower()
        parsed.append({
            'name': name,
            'amount': amount,
            'unit': unit
        })

    return parsed


# 2. JSON 데이터 로딩
with open("filtered_supplements_with_raw_line.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. 전체 상품에 대해 raw_line 기반 파싱
for item in tqdm(data):
    raw_lines = []

    # raw_line이 supplement_facts 안에 리스트로 있을 수 있음
    if 'supplement_facts' in item:
        for fact in item['supplement_facts']:
            if isinstance(fact, dict) and 'raw_line' in fact:
                raw_lines.append(fact['raw_line'])

    # 하나라도 있으면 파싱
    parsed_ingredients = []
    for raw in raw_lines:
        parsed_ingredients.extend(parse_supplement_facts_from_raw_line(raw))

    # 중복 제거 (성분명 + 단위 기준)
    unique = {}
    for p in parsed_ingredients:
        key = (p['name'].lower(), p['unit'])
        if key not in unique:
            unique[key] = p

    item['parsed_ingredients'] = list(unique.values())

# 4. 결과 저장
with open("parsed_supplements_output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 파싱 완료! 'parsed_supplements_output.json' 파일로 저장되었습니다.")