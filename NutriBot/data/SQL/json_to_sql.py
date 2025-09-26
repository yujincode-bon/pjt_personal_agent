import json
import psycopg2

# 1. DB 연결 설정
conn = psycopg2.connect(
    host="localhost",
    database="NutriBot",     # 본인 DB 이름
    user="postgres",              # 본인 사용자명
    password="67368279",     # 본인 비밀번호
    port="5432"                   # 기본 포트 (변경했으면 수정)
)
cur = conn.cursor()

# 2. JSON 파일 열기
# ✅ 데이터 소스를 새로 파싱된 파일로 변경합니다.
with open("/Users/gim-yujin/Desktop/pjt_personal_agent/NutriBot/data/json/parsed_supplements_output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 3. 제품/성분/리뷰 입력
for item in data:
    # 1) supplements 테이블 입력
    title = item.get("title")
    brand = item.get("brand")
    form = item.get("form")
    servings_per_container = item.get("servings_per_container")
    serving_size_value = item.get("serving_size_value")
    serving_size_unit = item.get("serving_size_unit")
    price = item.get("price")
    currency = item.get("currency")
    upc = item.get("UPC Code") or item.get("upc")
    product_code = item.get("Product code") or item.get("Pid")
    source_url = item.get("url") or item.get("P url")

    cur.execute("""
        INSERT INTO supplements (name, brand, form, servings_per_container, serving_size_value, 
        serving_size_unit, price, currency, upc, product_code, source_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING supplement_id
    """, (
        title, brand, form, servings_per_container, serving_size_value,
        serving_size_unit, price, currency, upc, product_code, source_url
    ))

    supplement_id = cur.fetchone()[0]

    # 2) ✅ 'parsed_ingredients'를 우선적으로 사용하고, 없을 경우 'supplement_facts'를 대체로 사용합니다.
    supplement_facts = item.get("parsed_ingredients") or item.get("supplement_facts", [])

    for fact in supplement_facts:
        name = fact.get("name")
        amount = fact.get("amount")
        unit = fact.get("unit")
        percent_dv = fact.get("percent_dv")

        if not name or amount is None:
            continue

        # ingredients 테이블에 존재하는지 확인 후 없으면 추가
        cur.execute("SELECT ingredient_id FROM ingredients WHERE name = %s", (name,))
        result = cur.fetchone()
        if result:
            ingredient_id = result[0]
        else:
            cur.execute("INSERT INTO ingredients (name) VALUES (%s) RETURNING ingredient_id", (name,))
            ingredient_id = cur.fetchone()[0]

        # supplement_ingredients 삽입
        cur.execute("""
            INSERT INTO supplement_ingredients (supplement_id, ingredient_id, amount_per_serving, amount_unit, percent_dv)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (supplement_id, ingredient_id) DO NOTHING
        """, (
            supplement_id, ingredient_id, amount,
            unit if unit else None,
            percent_dv if percent_dv else None
        ))

    # 3) review_stats 테이블 입력
    avg_rating = item.get("avg_rating")
    reviews_count = item.get("reviews_count")

    if avg_rating or reviews_count:
        cur.execute("""
            INSERT INTO review_stats (supplement_id, avg_rating, reviews_count)
            VALUES (%s, %s, %s)
            ON CONFLICT (supplement_id) DO UPDATE 
            SET avg_rating = EXCLUDED.avg_rating,
                reviews_count = EXCLUDED.reviews_count
        """, (
            supplement_id,
            float(avg_rating) if avg_rating else None,
            int(reviews_count) if reviews_count else None
        ))

# 4. 커밋 및 종료
conn.commit()
cur.close()
conn.close()

print("✅ JSON → PostgreSQL 데이터 입력 완료!")