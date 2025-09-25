from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Active 데이터 확인
cursor.execute('SELECT COUNT(*) as count FROM hotels WHERE is_active = true')
result = cursor.fetchone()
print('Active hotels:', result['count'])

cursor.execute('SELECT COUNT(*) as count FROM tours WHERE is_active = true')
result = cursor.fetchone()
print('Active tours:', result['count'])

# 실제 데이터 상태 확인
cursor.execute('SELECT hotel_name, is_active FROM hotels LIMIT 3')
for row in cursor.fetchall():
    print(f'Hotel: {row["hotel_name"]}, Active: {row["is_active"]}')

cursor.execute('SELECT tour_name, is_active FROM tours LIMIT 3')
for row in cursor.fetchall():
    print(f'Tour: {row["tour_name"]}, Active: {row["is_active"]}')

cursor.close()
conn.close()