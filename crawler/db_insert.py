import pymysql
import pandas as pd

# CSV 파일 읽기
df = pd.read_csv("C:\\projects\\mart-crawler\\cu_products.csv")
print(f"CSV 데이터 {len(df)}개 로딩 완료!")
print(df.head())

# MySQL 연결
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1234",
    database="mart_compare",
    charset="utf8mb4"
)

cursor = conn.cursor()

# 데이터 삽입
insert_sql = """
    INSERT INTO product (mart_id, name, price, event_type)
    VALUES (%s, %s, %s, %s)
"""

count = 0
for _, row in df.iterrows():
    # 가격에서 쉼표 제거 후 숫자로 변환 (예: "4,500" → 4500)
    price = int(str(row["가격"]).replace(",", ""))
    
    cursor.execute(insert_sql, (
        1,              # mart_id (CU = 1)
        row["상품명"],
        price,
        row["행사종류"]
    ))
    count += 1

conn.commit()
cursor.close()
conn.close()

print(f"\n✅ {count}개 상품 DB 삽입 완료!")