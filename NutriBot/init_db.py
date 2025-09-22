from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:67368279@localhost:5432/NutriBot")

with engine.connect() as conn:
    # 1️⃣ tsv 컬럼이 없으면 생성
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='supplements' AND column_name='tsv'
            ) THEN
                ALTER TABLE supplements ADD COLUMN tsv tsvector;
            END IF;
        END
        $$;
    """))

    # 2️⃣ title + description 기반으로 tsv 값 채우기
    conn.execute(text("""
        UPDATE supplements
        SET tsv = to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(description, ''));
    """))

    # 3️⃣ 인덱스도 없으면 생성
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_supp_tsv ON supplements USING GIN (tsv);
    """))

print("✅ tsv 컬럼 수동 생성 및 인덱스 완료")