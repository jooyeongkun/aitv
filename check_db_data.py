import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def check_database_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'chat_consulting'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASS', 'your_password'),
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        
        print("=== 호텔 지역별 데이터 ===")
        cursor.execute("SELECT DISTINCT hotel_region, COUNT(*) as count FROM hotels WHERE is_active = true GROUP BY hotel_region ORDER BY hotel_region")
        hotels = cursor.fetchall()
        for hotel in hotels:
            print(f"{hotel['hotel_region']}: {hotel['count']}개")
        
        print("\n=== 투어 지역별 데이터 ===")
        cursor.execute("SELECT DISTINCT tour_region, COUNT(*) as count FROM tours WHERE is_active = true GROUP BY tour_region ORDER BY tour_region")
        tours = cursor.fetchall()
        for tour in tours:
            print(f"{tour['tour_region']}: {tour['count']}개")
            
        print("\n=== 샘플 데이터 확인 ===")
        cursor.execute("SELECT hotel_name, hotel_region FROM hotels WHERE is_active = true LIMIT 3")
        sample_hotels = cursor.fetchall()
        print("호텔 샘플:")
        for hotel in sample_hotels:
            print(f"- {hotel['hotel_name']} ({hotel['hotel_region']})")
            
        cursor.execute("SELECT tour_name, tour_region FROM tours WHERE is_active = true LIMIT 3")
        sample_tours = cursor.fetchall()
        print("\n투어 샘플:")
        for tour in sample_tours:
            print(f"- {tour['tour_name']} ({tour['tour_region']})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")

if __name__ == "__main__":
    check_database_data()