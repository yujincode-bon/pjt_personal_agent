from sqlalchemy import create_engine, text

# ✅ PostgreSQL 연결
engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")

with engine.connect() as conn:
    print("🔌 PostgreSQL 연결 시도 중...")

    # ✅ 현재 연결된 DB 확인
    db_name = conn.execute(text("SELECT current_database();")).scalar()
    print(f"🗂 현재 접속된 데이터베이스: {db_name}")

    # ✅ supplements 테이블 컬럼 조회
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'supplements'
        AND table_schema = 'public';
    """))

    columns = result.fetchall()
    print(f"\n📋 총 {len(columns)}개의 컬럼이 조회되었습니다:")

    has_tsv = False
    for row in columns:
        mark = "✅" if row.column_name == "tsv" else "🔹"
        if row.column_name == "tsv":
            has_tsv = True
        print(f"{mark} {row.column_name} ({row.data_type})")

    if has_tsv:
        print("\n🟢 `tsv` 컬럼이 존재합니다. 추천 기능 정상 작동 가능! ✅")
    else:
        print("\n❗ `tsv` 컬럼이 존재하지 않습니다. `init_db.py`를 다시 확인해주세요.")