from supabase_db import SupabaseDB

def add_all_data():
    db = SupabaseDB()
    
    # 연결 테스트
    if not db.connect():
        print("Failed to connect to Supabase")
        return
    
    print("Connected to Supabase successfully")
    
    # 패키지 데이터
    packages = [
        {
            "name": "제주도 3박4일 힐링투어",
            "destination": "제주도", 
            "duration": 4,
            "price": 450000,
            "category": "힐링여행",
            "description": "제주도의 자연을 만끽하는 힐링 여행",
            "includes": "항공료, 호텔, 렌터카, 관광지 입장료"
        },
        {
            "name": "부산 2박3일 바다여행",
            "destination": "부산",
            "duration": 3, 
            "price": 320000,
            "category": "바다여행",
            "description": "부산 바다와 맛집을 즐기는 여행",
            "includes": "KTX, 호텔, 식사 2회"
        },
        {
            "name": "강릉 1박2일 동해여행", 
            "destination": "강릉",
            "duration": 2,
            "price": 180000,
            "category": "단기여행", 
            "description": "동해 바다를 보며 힐링하는 여행",
            "includes": "교통비, 펜션, 조식"
        },
        {
            "name": "경주 문화유산투어",
            "destination": "경주",
            "duration": 2,
            "price": 220000,
            "category": "문화여행",
            "description": "경주 역사 유적지 탐방",
            "includes": "버스, 호텔, 가이드, 입장료"
        }
    ]
    
    # 호텔 데이터
    hotels = [
        {
            "name": "제주 오션뷰 리조트",
            "city": "제주도",
            "star_rating": 5,
            "price_per_night": 280000,
            "amenities": "오션뷰, 스파, 수영장, 골프장",
            "description": "제주 바다가 보이는 최고급 리조트",
            "address": "제주시 애월읍",
            "phone": "064-111-2222"
        },
        {
            "name": "부산 해운대 호텔",
            "city": "부산", 
            "star_rating": 4,
            "price_per_night": 180000,
            "amenities": "해변접근, 레스토랑, 사우나",
            "description": "해운대 해변 바로 앞 호텔",
            "address": "부산 해운대구",
            "phone": "051-222-3333"
        },
        {
            "name": "강릉 바다펜션",
            "city": "강릉",
            "star_rating": 3,
            "price_per_night": 120000,
            "amenities": "바다뷰, 바베큐장, 주방",
            "description": "동해바다 앞 아늑한 펜션",
            "address": "강릉시 사천면",
            "phone": "033-333-4444"
        },
        {
            "name": "경주 한옥호텔",
            "city": "경주",
            "star_rating": 4,
            "price_per_night": 150000,
            "amenities": "한옥체험, 전통정원, 한복대여", 
            "description": "전통 한옥 스타일의 특급호텔",
            "address": "경주시 중앙로",
            "phone": "054-444-5555"
        },
        {
            "name": "서울 비즈니스호텔",
            "city": "서울",
            "star_rating": 4,
            "price_per_night": 200000,
            "amenities": "지하철역 직결, 비즈니스센터",
            "description": "서울 중심가 비즈니스호텔", 
            "address": "서울 중구 명동",
            "phone": "02-555-6666"
        }
    ]
    
    # 패키지 데이터 추가
    print("Adding packages...")
    for i, package in enumerate(packages, 1):
        try:
            result = db.add_package(package)
            print(f"{i}. Package added: {result}")
        except Exception as e:
            print(f"{i}. Package error: {str(e)}")
    
    # 호텔 데이터 추가  
    print("\\nAdding hotels...")
    for i, hotel in enumerate(hotels, 1):
        try:
            result = db.add_hotel(hotel) 
            print(f"{i}. Hotel added: {result}")
        except Exception as e:
            print(f"{i}. Hotel error: {str(e)}")
    
    print("\\nData insertion completed!")

if __name__ == "__main__":
    add_all_data()