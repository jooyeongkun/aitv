"""
Supabase 데이터베이스 테이블 생성 및 초기 데이터 입력
"""
from supabase_db import SupabaseDB
from datetime import datetime

def create_tables_and_data():
    """Supabase에 테이블 생성 및 초기 데이터 입력"""
    db = SupabaseDB()
    
    print("Connecting to Supabase...")
    
    # 샘플 패키지 데이터
    packages = [
        {
            "name": "제주도 3박4일 패키지",
            "destination": "제주도",
            "duration": 4,
            "price": 450000,
            "category": "국내여행",
            "description": "제주도의 아름다운 자연을 만끽할 수 있는 3박 4일 패키지입니다. 성산일출봉, 한라산, 우도 등 주요 관광지를 포함합니다.",
            "includes": "항공료, 호텔, 렌터카, 주요 관광지 입장료"
        },
        {
            "name": "부산 2박3일 미식투어",
            "destination": "부산",
            "duration": 3,
            "price": 320000,
            "category": "미식여행",
            "description": "부산의 신선한 해산물과 전통 음식을 맛보는 미식 투어입니다.",
            "includes": "KTX, 호텔, 식사, 현지 가이드"
        },
        {
            "name": "강릉 바다여행 2박3일",
            "destination": "강릉",
            "duration": 3,
            "price": 280000,
            "category": "휴양여행",
            "description": "동해의 푸른 바다와 해변을 즐기는 힐링 여행입니다.",
            "includes": "교통비, 숙박, 해변 액티비티"
        },
        {
            "name": "경주 역사문화 투어",
            "destination": "경주",
            "duration": 2,
            "price": 180000,
            "category": "문화여행",
            "description": "천년 고도 경주의 역사와 문화를 체험하는 투어입니다.",
            "includes": "교통비, 숙박, 문화재 관람료, 가이드"
        }
    ]
    
    # 샘플 호텔 데이터  
    hotels = [
        {
            "name": "제주 그랜드 호텔",
            "city": "제주도",
            "star_rating": 5,
            "price_per_night": 200000,
            "amenities": "오션뷰, 스파, 수영장, 피트니스센터",
            "description": "제주도 최고급 리조트 호텔로 바다 전망이 아름다운 곳",
            "address": "제주시 연동",
            "phone": "064-123-4567"
        },
        {
            "name": "부산 비즈니스 호텔",
            "city": "부산",
            "star_rating": 4,
            "price_per_night": 150000,
            "amenities": "비즈니스센터, 레스토랑, 주차장",
            "description": "부산 중심가에 위치한 비즈니스 호텔",
            "address": "부산 해운대구",
            "phone": "051-234-5678"
        },
        {
            "name": "강릉 오션뷰 호텔",
            "city": "강릉",
            "star_rating": 4,
            "price_per_night": 180000,
            "amenities": "바다전망, 조식 포함, 커피라운지",
            "description": "동해바다가 보이는 아늑한 호텔",
            "address": "강릉시 사천면",
            "phone": "033-345-6789"
        },
        {
            "name": "경주 한옥스테이",
            "city": "경주",
            "star_rating": 3,
            "price_per_night": 120000,
            "amenities": "전통 한옥, 한복 체험, 전통차",
            "description": "경주 전통 문화를 체험할 수 있는 한옥 숙소",
            "address": "경주시 황남동",
            "phone": "054-456-7890"
        },
        {
            "name": "전주 게스트하우스",
            "city": "전주",
            "star_rating": 3,
            "price_per_night": 80000,
            "amenities": "한옥마을 접근성, 공용 주방, WiFi",
            "description": "한옥마을 근처의 깔끔한 게스트하우스",
            "address": "전주시 완산구",
            "phone": "063-567-8901"
        }
    ]
    
    print("Adding packages to Supabase...")
    for package in packages:
        try:
            result = db.add_package(package)
            if result:
                print(f"Added package: {package['name']}")
            else:
                print(f"Failed to add package: {package['name']}")
        except Exception as e:
            print(f"Error adding package {package['name']}: {e}")
    
    print("\\nAdding hotels to Supabase...")
    for hotel in hotels:
        try:
            result = db.add_hotel(hotel)
            if result:
                print(f"Added hotel: {hotel['name']}")
            else:
                print(f"Failed to add hotel: {hotel['name']}")
        except Exception as e:
            print(f"Error adding hotel {hotel['name']}: {e}")
    
    print("\\nSupabase setup completed!")
    print("You can now view and manage data at: https://nqxlbxwkgaxrqubadblh.supabase.co")

if __name__ == "__main__":
    create_tables_and_data()