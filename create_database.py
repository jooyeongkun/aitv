"""
여행사 데이터베이스 생성 스크립트
"""
import sqlite3
from datetime import datetime

def create_database():
    """여행사 데이터베이스와 테이블 생성"""
    conn = sqlite3.connect('travel_consultation.db')
    cursor = conn.cursor()
    
    # 1. 여행 패키지 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        destination TEXT NOT NULL,
        category TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        price INTEGER NOT NULL,
        description TEXT,
        inclusions TEXT,
        exclusions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. 호텔 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        star_rating INTEGER NOT NULL,
        price_per_night INTEGER NOT NULL,
        amenities TEXT,
        description TEXT,
        address TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 3. 상담 세션 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultation_sessions (
        id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 4. 상담 메시지 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultation_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES consultation_sessions (id)
    )
    ''')
    
    # 5. 고객 문의 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customer_inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        inquiry_type TEXT, -- package, hotel, general
        target_id INTEGER, -- package_id or hotel_id
        inquiry_text TEXT,
        status TEXT DEFAULT 'pending', -- pending, answered, closed
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다!")
    return conn

def insert_sample_data():
    """샘플 데이터 입력"""
    conn = sqlite3.connect('travel_consultation.db')
    cursor = conn.cursor()
    
    # 패키지 데이터 삭제 후 재입력
    cursor.execute('DELETE FROM packages')
    
    packages = [
        ("제주도 3박4일 힐링 패키지", "제주도", "힐링", 4, 500000, 
         "제주도의 아름다운 자연 속에서 힐링하는 특별한 여행", 
         "항공료, 렌터카, 관광지 입장료, 가이드 서비스", 
         "숙박비, 식사비, 개인 경비"),
        
        ("부산 2박3일 관광 패키지", "부산", "관광", 3, 300000, 
         "부산의 대표 관광지를 둘러보는 알찬 여행", 
         "KTX 왕복, 시내 교통비, 주요 관광지 입장료", 
         "숙박비, 식사비, 쇼핑비용"),
         
        ("강릉 바다 2박3일 패키지", "강릉", "자연", 3, 400000, 
         "동해 바다와 커피의 도시 강릉 여행", 
         "KTX 왕복, 해변 액티비티, 커피 체험", 
         "숙박비, 식사비, 추가 액티비티"),
         
        ("경주 역사문화 3박4일 패키지", "경주", "문화", 4, 450000, 
         "천년 고도 경주의 역사와 문화를 체험하는 여행", 
         "교통비, 문화재 관람료, 전통체험 비용", 
         "숙박비, 식사비, 기념품 구입비"),
         
        ("전주 한옥마을 1박2일 패키지", "전주", "문화", 2, 250000, 
         "전주 한옥마을에서 전통문화를 체험하는 짧은 여행", 
         "KTX 왕복, 한옥마을 체험, 전통차 체험", 
         "숙박비, 식사비, 쇼핑비용")
    ]
    
    cursor.executemany('''
    INSERT INTO packages (name, destination, category, duration_days, price, description, inclusions, exclusions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', packages)
    
    # 호텔 데이터 삭제 후 재입력
    cursor.execute('DELETE FROM hotels')
    
    hotels = [
        ("제주 그랜드 호텔", "제주도", 5, 200000, 
         "오션뷰, 스파, 수영장, 피트니스센터", 
         "제주도 최고급 리조트 호텔로 바다 전망이 아름다운 곳", 
         "제주시 연동", "064-123-4567"),
         
        ("부산 비즈니스 호텔", "부산", 4, 150000, 
         "비즈니스센터, 레스토랑, 주차장", 
         "부산 중심가에 위치한 비즈니스 호텔", 
         "부산 해운대구", "051-234-5678"),
         
        ("강릉 오션뷰 호텔", "강릉", 4, 180000, 
         "바다전망, 조식 포함, 커피라운지", 
         "동해바다가 보이는 아늑한 호텔", 
         "강릉시 사천면", "033-345-6789"),
         
        ("경주 한옥스테이", "경주", 3, 120000, 
         "전통 한옥, 한복 체험, 전통차", 
         "경주 전통 문화를 체험할 수 있는 한옥 숙소", 
         "경주시 황남동", "054-456-7890"),
         
        ("전주 게스트하우스", "전주", 3, 80000, 
         "한옥마을 접근성, 공용 주방, WiFi", 
         "한옥마을 근처의 깔끔한 게스트하우스", 
         "전주시 완산구", "063-567-8901")
    ]
    
    cursor.executemany('''
    INSERT INTO hotels (name, city, star_rating, price_per_night, amenities, description, address, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', hotels)
    
    conn.commit()
    print("✅ 샘플 데이터가 성공적으로 입력되었습니다!")
    
    # 입력된 데이터 확인
    cursor.execute('SELECT COUNT(*) FROM packages')
    package_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM hotels')
    hotel_count = cursor.fetchone()[0]
    
    print(f"📦 패키지 상품: {package_count}개")
    print(f"🏨 호텔 정보: {hotel_count}개")
    
    conn.close()

if __name__ == "__main__":
    print("🗄️ 여행사 데이터베이스 생성 시작...")
    create_database()
    insert_sample_data()
    print("🎉 데이터베이스 구축 완료!")