from database import get_db_connection
import sys

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

conn = get_db_connection()
cursor = conn.cursor()

# 투어 테이블 스키마 확인
print("=== TOURS TABLE SCHEMA ===")
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'tours'
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"Column: {row['column_name']}, Type: {row['data_type']}, Nullable: {row['is_nullable']}")

print("\n=== HOTELS TABLE SCHEMA ===")
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'hotels'
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"Column: {row['column_name']}, Type: {row['data_type']}, Nullable: {row['is_nullable']}")

print("\n=== SAMPLE TOURS DATA ===")
cursor.execute("SELECT * FROM tours WHERE is_active = true LIMIT 2")
tours = cursor.fetchall()
for tour in tours:
    print("Tour:", dict(tour))

print("\n=== SAMPLE HOTELS DATA ===")
cursor.execute("SELECT * FROM hotels WHERE is_active = true LIMIT 2")
hotels = cursor.fetchall()
for hotel in hotels:
    print("Hotel:", dict(hotel))

cursor.close()
conn.close()